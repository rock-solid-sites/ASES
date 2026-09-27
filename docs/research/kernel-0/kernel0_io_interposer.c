/* Test-only Linux interposer. Never link into the reference service normally. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <limits.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

static _Atomic unsigned long sequence = 0;

static void *next_symbol(const char *name) {
    dlerror();
    void *symbol = dlsym(RTLD_NEXT, name);
    if (dlerror() != NULL || symbol == NULL) _exit(121);
    return symbol;
}

static int target(const char *path) {
    const char *prefix = getenv("K0_IO_DIRECTORY");
    if (prefix == NULL) return 0;
    size_t length = strlen(prefix);
    return strncmp(path, prefix, length) == 0 &&
           (path[length] == '/' || path[length] == '\0');
}

static int fd_path(int fd, char *path) {
    char descriptor[64];
    int saved = errno;
    snprintf(descriptor, sizeof(descriptor), "/proc/self/fd/%d", fd);
    ssize_t n = readlink(descriptor, path, PATH_MAX - 1);
    if (n >= 0) path[n] = '\0';
    errno = saved;
    return n >= 0 && target(path);
}

static void point(const char *op, const char *phase, const char *path,
                  long long offset, size_t size, long long result) {
    int saved = errno;
    if (!target(path)) return;
    const char *event_text = getenv("K0_IO_EVENT_FD");
    const char *release_text = getenv("K0_IO_RELEASE_FD");
    const char *cut_text = getenv("K0_IO_CUT");
    if (!event_text || !release_text || !cut_text) _exit(122);
    unsigned long n = atomic_fetch_add(&sequence, 1) + 1;
    const char *prefix = getenv("K0_IO_DIRECTORY");
    const char *file = path + strlen(prefix);
    if (*file == '/') ++file;
    if (*file == '\0') file = ".";
    char line[1024];
    int bytes = snprintf(line, sizeof(line),
        "{\"index\":%lu,\"op\":\"%s\",\"phase\":\"%s\",\"file\":\"%s\","
        "\"offset\":%lld,\"size\":%zu,\"result\":%lld}\n",
        n, op, phase, file, offset, size, result);
    if (bytes <= 0 || (size_t)bytes >= sizeof(line)) _exit(123);
    int event_fd = atoi(event_text);
    if (write(event_fd, line, (size_t)bytes) != bytes) _exit(124);
    if (n == strtoul(cut_text, NULL, 10)) {
        char release;
        /* Parent kills the process at this point; no synthetic error returned. */
        if (read(atoi(release_text), &release, 1) != 1) _exit(125);
    }
    errno = saved;
}

static size_t split_size(size_t requested) {
    const char *at = getenv("K0_IO_SPLIT_AT");
    const char *bytes = getenv("K0_IO_SPLIT_BYTES");
    if (!at || !bytes || strtoul(at, NULL, 10) != atomic_load(&sequence)) return 0;
    size_t partial = strtoul(bytes, NULL, 10);
    return partial > 0 && partial < requested ? partial : 0;
}

ssize_t pwrite(int fd, const void *buf, size_t size, off_t offset) {
    ssize_t (*real_call)(int, const void *, size_t, off_t) = next_symbol("pwrite");
    char path[PATH_MAX];
    int track = fd_path(fd, path);
    if (track) point("pwrite", "before", path, offset, size, -999);
    size_t partial = track ? split_size(size) : 0;
    ssize_t result;
    if (partial) {
        ssize_t first = real_call(fd, buf, partial, offset);
        point("pwrite", "partial", path, offset, partial, first);
        if (first != (ssize_t)partial) return first;
        ssize_t second = real_call(fd, (const char *)buf + partial, size - partial, offset + partial);
        result = second < 0 ? first : first + second;
    } else {
        result = real_call(fd, buf, size, offset);
    }
    if (track) point("pwrite", "after", path, offset, size, result);
    return result;
}

ssize_t pwrite64(int fd, const void *buf, size_t size, off64_t offset) {
    ssize_t (*real_call)(int, const void *, size_t, off64_t) = next_symbol("pwrite64");
    char path[PATH_MAX];
    int track = fd_path(fd, path);
    if (track) point("pwrite64", "before", path, offset, size, -999);
    size_t partial = track ? split_size(size) : 0;
    ssize_t result;
    if (partial) {
        ssize_t first = real_call(fd, buf, partial, offset);
        point("pwrite64", "partial", path, offset, partial, first);
        if (first != (ssize_t)partial) return first;
        ssize_t second = real_call(fd, (const char *)buf + partial, size - partial, offset + partial);
        result = second < 0 ? first : first + second;
    } else {
        result = real_call(fd, buf, size, offset);
    }
    if (track) point("pwrite64", "after", path, offset, size, result);
    return result;
}

#define SYNC_WRAPPER(name) \
int name(int fd) { \
    int (*real_call)(int) = next_symbol(#name); \
    char path[PATH_MAX]; \
    int track = fd_path(fd, path); \
    if (track) point(#name, "before", path, 0, 0, -999); \
    int result = real_call(fd); \
    if (track) point(#name, "after", path, 0, 0, result); \
    return result; \
}

SYNC_WRAPPER(fsync)
SYNC_WRAPPER(fdatasync)

int ftruncate(int fd, off_t length) {
    int (*real_call)(int, off_t) = next_symbol("ftruncate");
    char path[PATH_MAX];
    int track = fd_path(fd, path);
    if (track) point("ftruncate", "before", path, length, 0, -999);
    int result = real_call(fd, length);
    if (track) point("ftruncate", "after", path, length, 0, result);
    return result;
}

int ftruncate64(int fd, off64_t length) {
    int (*real_call)(int, off64_t) = next_symbol("ftruncate64");
    char path[PATH_MAX];
    int track = fd_path(fd, path);
    if (track) point("ftruncate64", "before", path, length, 0, -999);
    int result = real_call(fd, length);
    if (track) point("ftruncate64", "after", path, length, 0, result);
    return result;
}

int unlink(const char *path) {
    int (*real_call)(const char *) = next_symbol("unlink");
    int track = target(path);
    if (track) point("unlink", "before", path, 0, 0, -999);
    int result = real_call(path);
    if (track) point("unlink", "after", path, 0, 0, result);
    return result;
}
