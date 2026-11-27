#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/inotify.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define FULL_VERSION "full (eazy 5.2.0 rev.56)"
#define MAX_WATCH_ID 1048576
#define EVENT_BUF_LEN (64 * 1024)
#define DEFAULT_QUEUE "/dev/shm/fila_eventos"

static int opt_hidden = 0;
static int opt_only = 0;
static int opt_recursive = 1;
static int opt_start = 0;
static int debug_mode = 0;
static int inotify_fd = -1;
static int watch_count = 0;
static unsigned long long seq_evento = 0;
static char *watches[MAX_WATCH_ID];
static char root_path[PATH_MAX];
static char exclude_path[PATH_MAX];
static char queue_path[PATH_MAX];
static dev_t root_device;
static volatile sig_atomic_t running = 1;

static void stop_monitor(int sig) {
    (void)sig;
    running = 0;
}

static int path_is_within(const char *path, const char *base) {
    size_t n;
    if (!path || !base || !*base) return 0;
    n = strlen(base);
    if (strncmp(path, base, n) != 0) return 0;
    return path[n] == '\0' || (n == 1 && base[0] == '/') || path[n] == '/';
}

static int should_ignore_name(const char *name) {
    return !opt_hidden && name && name[0] == '.';
}

static int should_ignore_path(const char *path) {
    if (!path) return 1;
    if (exclude_path[0] && path_is_within(path, exclude_path)) return 1;
    return 0;
}

static int write_all(int fd, const void *buf, size_t len) {
    const char *p = (const char *)buf;
    while (len) {
        ssize_t n = write(fd, p, len);
        if (n < 0) {
            if (errno == EINTR) continue;
            return -1;
        }
        p += n;
        len -= (size_t)n;
    }
    return 0;
}

/* Ticket binário: um byte de operação, NUL, caminho em bytes, NUL.
   Não depende de separadores, tabs, barras verticais nem quebras de linha no nome. */
static void queue_event(char op, const char *path) {
    char tmp[PATH_MAX * 2];
    char final[PATH_MAX * 2];
    int fd;
    size_t n;
    if (!opt_start || !path || !*path) return;
    seq_evento++;
    if (snprintf(tmp, sizeof(tmp), "%s/%ld_%llu.tmp", queue_path,
                 (long)getpid(), seq_evento) >= (int)sizeof(tmp)) return;
    if (snprintf(final, sizeof(final), "%s/%ld_%llu.evt", queue_path,
                 (long)getpid(), seq_evento) >= (int)sizeof(final)) return;
    fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC, 0600);
    if (fd < 0) return;
    n = strlen(path);
    if (write_all(fd, &op, 1) == 0 && write_all(fd, "\0", 1) == 0 &&
        write_all(fd, path, n) == 0 && write_all(fd, "\0", 1) == 0) {
        if (close(fd) == 0) {
            if (rename(tmp, final) == 0) return;
        } else {
            unlink(tmp);
            return;
        }
    } else {
        close(fd);
    }
    unlink(tmp);
}

static void display_event(const char *label, const char *path) {
    struct stat st;
    if (opt_start || !path) return;
    if (stat(path, &st) == 0) {
        printf("%-8s | %-10lld | %lld | %s\n", label,
               (long long)st.st_size, (long long)st.st_mtime, path);
    } else {
        printf("%-8s | %-10s | %lld | %s\n", label, "0", (long long)time(NULL), path);
    }
    fflush(stdout);
}

static void emit_event(char op, const char *label, const char *path) {
    if (!path || should_ignore_path(path)) return;
    if (opt_start) queue_event(op, path);
    else display_event(label, path);
}

static void remove_watch(int wd) {
    if (wd < 0 || wd >= MAX_WATCH_ID || !watches[wd]) return;
    if (debug_mode && !opt_start) fprintf(stderr, "[DEBUG -WATCH] %s\n", watches[wd]);
    free(watches[wd]);
    watches[wd] = NULL;
    if (watch_count > 0) watch_count--;
}

static void remove_watches_below(const char *base) {
    int wd;
    size_t n = strlen(base);
    for (wd = 0; wd < MAX_WATCH_ID; wd++) {
        if (!watches[wd]) continue;
        if (strncmp(watches[wd], base, n) == 0 &&
            (watches[wd][n] == '\0' || watches[wd][n] == '/')) {
            if (inotify_fd >= 0) (void)inotify_rm_watch(inotify_fd, wd);
            remove_watch(wd);
        }
    }
}

static void add_watch(int fd, const char *path) {
    uint32_t mask = IN_CREATE | IN_CLOSE_WRITE | IN_MODIFY | IN_ATTRIB |
                    IN_DELETE | IN_MOVED_TO | IN_MOVED_FROM |
                    IN_DELETE_SELF | IN_MOVE_SELF | IN_ONLYDIR;
    int wd;
    char *copy;
    if (should_ignore_path(path)) return;
    wd = inotify_add_watch(fd, path, mask);
    if (wd < 0 || wd >= MAX_WATCH_ID) return;
    copy = strdup(path);
    if (!copy) return;
    if (watches[wd]) free(watches[wd]);
    else watch_count++;
    watches[wd] = copy;
    if (debug_mode && !opt_start) fprintf(stderr, "[DEBUG +WATCH] %s\n", path);
}

static void add_tree(int fd, const char *path) {
    DIR *dir;
    struct dirent *entry;
    struct stat st;
    char child[PATH_MAX];
    if (should_ignore_path(path) || lstat(path, &st) != 0 || !S_ISDIR(st.st_mode)) return;
    if (st.st_dev != root_device) return;
    add_watch(fd, path);
    if (opt_only || !opt_recursive) return;
    dir = opendir(path);
    if (!dir) return;
    while ((entry = readdir(dir)) != NULL) {
        int n;
        if (!strcmp(entry->d_name, ".") || !strcmp(entry->d_name, "..")) continue;
        if (should_ignore_name(entry->d_name)) continue;
        n = snprintf(child, sizeof(child), "%s/%s", path, entry->d_name);
        if (n < 0 || n >= (int)sizeof(child)) continue;
        if (should_ignore_path(child)) continue;
        if (lstat(child, &st) == 0 && S_ISDIR(st.st_mode) && st.st_dev == root_device)
            add_tree(fd, child);
    }
    closedir(dir);
}

static int queue_init(void) {
    struct stat st;
    if (mkdir(queue_path, 0700) != 0 && errno != EEXIST) return -1;
    if (stat(queue_path, &st) != 0 || !S_ISDIR(st.st_mode)) return -1;
    if (st.st_uid != getuid()) {
        errno = EACCES;
        return -1;
    }
    (void)chmod(queue_path, 0700);
    return 0;
}

static void print_help(const char *program) {
    printf("Uso: %s [diretorio] [/h] [/o | /s] [/start] [--queue DIR] [--exclude DIR]\n\n", program);
    printf("  /h             inclui arquivos e pastas ocultos\n");
    printf("  /o             monitora somente a pasta raiz, sem recursao\n");
    printf("  /s             monitora recursivamente (padrao)\n");
    printf("  /start         grava tickets .evt para consumo pelo Easy\n");
    printf("  --queue DIR    fila privada de eventos (padrao: %s)\n", DEFAULT_QUEUE);
    printf("  --exclude DIR  ignora esta pasta e seus descendentes\n");
}

int main(int argc, char **argv) {
    const char *arg_root = NULL;
    int i;
    struct sigaction sa;
    struct stat st;
    union {
        struct inotify_event align;
        char bytes[EVENT_BUF_LEN];
    } buffer;

    snprintf(queue_path, sizeof(queue_path), "%s", DEFAULT_QUEUE);
    for (i = 1; i < argc; i++) {
        if (!strcasecmp(argv[i], "--version") || !strcasecmp(argv[i], "/v")) {
            puts(FULL_VERSION);
            return 0;
        } else if (!strcasecmp(argv[i], "--help") || !strcmp(argv[i], "/?")) {
            print_help(argv[0]);
            return 0;
        } else if (!strcasecmp(argv[i], "/h")) {
            opt_hidden = 1;
        } else if (!strcasecmp(argv[i], "/o")) {
            opt_only = 1;
            opt_recursive = 0;
        } else if (!strcasecmp(argv[i], "/s")) {
            opt_only = 0;
            opt_recursive = 1;
        } else if (!strcasecmp(argv[i], "/start")) {
            opt_start = 1;
        } else if (!strcmp(argv[i], "--queue") && i + 1 < argc) {
            snprintf(queue_path, sizeof(queue_path), "%s", argv[++i]);
            opt_start = 1;
        } else if (!strcmp(argv[i], "--exclude") && i + 1 < argc) {
            char resolved[PATH_MAX];
            if (realpath(argv[++i], resolved)) snprintf(exclude_path, sizeof(exclude_path), "%s", resolved);
        } else if (!strcmp(argv[i], "--debug")) {
            debug_mode = 1;
        } else if (!strcmp(argv[i], "--")) {
            if (i + 1 < argc) arg_root = argv[++i];
            break;
        } else {
            arg_root = argv[i];
        }
    }
    if (!arg_root) arg_root = ".";
    if (!realpath(arg_root, root_path)) {
        perror("realpath(root)");
        return 2;
    }
    if (lstat(root_path, &st) != 0 || !S_ISDIR(st.st_mode)) {
        fprintf(stderr, "A raiz nao e um diretorio: %s\n", root_path);
        return 2;
    }
    root_device = st.st_dev;
    if (exclude_path[0] && path_is_within(root_path, exclude_path)) {
        fprintf(stderr, "A raiz esta dentro do caminho excluido.\n");
        return 2;
    }
    if (opt_start && queue_init() != 0) {
        perror("fila de eventos");
        return 3;
    }
    inotify_fd = inotify_init1(IN_CLOEXEC);
    if (inotify_fd < 0) {
        perror("inotify_init1");
        return 4;
    }
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = stop_monitor;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    if (sigaction(SIGINT, &sa, NULL) != 0 || sigaction(SIGTERM, &sa, NULL) != 0) {
        perror("sigaction");
        close(inotify_fd);
        return 5;
    }
    add_tree(inotify_fd, root_path);
    if (!opt_start) {
        printf("=== %s ===\nRaiz: %s | modo: %s | watches: %d\nAguardando eventos...\n",
               FULL_VERSION, root_path, opt_only ? "somente raiz" : "recursivo", watch_count);
        fflush(stdout);
    }

    while (running) {
        ssize_t length = read(inotify_fd, buffer.bytes, sizeof(buffer.bytes));
        ssize_t offset = 0;
        if (length < 0) {
            if (errno == EINTR) continue;
            perror("read(inotify)");
            break;
        }
        while (offset < length) {
            struct inotify_event *event = (struct inotify_event *)(buffer.bytes + offset);
            if (event->mask & IN_Q_OVERFLOW) {
                emit_event('!', "RECONFERIR", root_path);
                offset += (ssize_t)sizeof(*event) + event->len;
                continue;
            }
            if (event->mask & IN_IGNORED) {
                remove_watch(event->wd);
                offset += (ssize_t)sizeof(*event) + event->len;
                continue;
            }
            if (event->wd >= 0 && event->wd < MAX_WATCH_ID && watches[event->wd]) {
                char full_path[PATH_MAX];
                const char *parent = watches[event->wd];
                int n;
                if (event->len && should_ignore_name(event->name)) {
                    offset += (ssize_t)sizeof(*event) + event->len;
                    continue;
                }
                if (event->len) n = snprintf(full_path, sizeof(full_path), "%s/%s", parent, event->name);
                else n = snprintf(full_path, sizeof(full_path), "%s", parent);
                if (n >= 0 && n < (int)sizeof(full_path) && !should_ignore_path(full_path)) {
                    int is_dir = (event->mask & IN_ISDIR) != 0;
                    if (event->len && is_dir) {
                        if (event->mask & (IN_CREATE | IN_MOVED_TO)) {
                            if (!opt_only && opt_recursive) add_tree(inotify_fd, full_path);
                            emit_event('D', "PASTA +", full_path);
                        }
                        if (event->mask & (IN_DELETE | IN_MOVED_FROM)) {
                            emit_event('R', "PASTA -", full_path);
                            remove_watches_below(full_path);
                        }
                    } else if (event->len) {
                        if (event->mask & (IN_DELETE | IN_MOVED_FROM))
                            emit_event('X', "REMOVIDO", full_path);
                        else if (event->mask & (IN_CREATE | IN_CLOSE_WRITE | IN_MODIFY | IN_MOVED_TO | IN_ATTRIB))
                            emit_event('U', "ATUALIZADO", full_path);
                    } else if (event->mask & (IN_DELETE_SELF | IN_MOVE_SELF)) {
                        emit_event('R', "PASTA -", full_path);
                        remove_watches_below(full_path);
                    }
                }
            }
            offset += (ssize_t)sizeof(*event) + event->len;
        }
    }
    close(inotify_fd);
    return 0;
}
