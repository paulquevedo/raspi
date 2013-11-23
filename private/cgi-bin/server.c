#include <fcgi_stdio.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#ifndef TRUE
#define TRUE 1
#endif
#ifndef FALSE
#define FALSE 0
#endif

#define ARRAY_SIZE(x) (sizeof(x)/sizeof(x[0]))

static char hostname[64];
static time_t server_start_time;

static void initialize(void)
{
    gethostname(hostname, sizeof(hostname)-1);
    hostname[64] = 0;
    server_start_time = time(0);
}

static void get_time_string(char *string, int len)
{
    time_t timer;
    struct tm *tm_info;

    time(&timer);
    tm_info = localtime(&timer);
    strftime(string, len, "%Y/%m/%d %H:%M:%S", tm_info);
}

static void get_uptime_string(char *string, int len)
{
    time_t uptime = time(0);

    memset(string, 0, len);

    if (len < 32)
        return;

    uptime = uptime - server_start_time;
    if (uptime > (3600 * 24)) {
        sprintf(string, "%d days", uptime / (3600 * 24));
        uptime %= (3600 * 24);
    }
    sprintf(string, "%s %02dh:%02dm:%02ds", string,
                                    uptime / 3600,
                                    (uptime % 3600) / 60,
                                    (uptime % 60));
}

static void resp_invalid_request(int http_status, char *msg)
{
    printf("Status: %d %s\r\n", http_status, msg);
}

static void resp_hostname(void)
{
    puts("Content-type: text/html\n");
    printf("%s\n", hostname);
}

static void resp_time(void)
{
    char time_str[32];
    get_time_string(time_str, sizeof(time_str));
    puts("Content-type: text/html\n");
    printf("%s", time_str);
}

static void resp_uptime(void)
{
    char uptime_str[32];
    get_uptime_string(uptime_str, sizeof(uptime_str));
    puts("Content-type: text/html\n");
    printf("%s", uptime_str);
}

static void resp_status_page(void)
{
    char uptime_str[32];
    char time_str[32];

    get_time_string(time_str, sizeof(time_str));
    get_uptime_string(uptime_str, sizeof(uptime_str));

    puts("Content-type: text/html\n");

    puts("<!DOCTYPE html>");
    puts("<head>");
    puts("  <meta charset=\"utf-8\">");
    puts("  <meta http-equiv=\"Refresh\" content=\"10\">");
    puts("<title>");
    printf("%s Status Page", hostname);
    puts("</title>");
    puts("</head>");
    puts("<body>");
    puts("<p>Server: OK</p>");
    printf("<p>%s</p>\n", time_str);
    printf("<p>Uptime: %s</p>", uptime_str);
    puts("</body>");
    puts("</html>");
}

typedef struct {
    char name[64];
    void (*fnPtr)(void);
} item_handlers_t;
static item_handlers_t item_handlers[] = {
    { "hostname",    resp_hostname },
    { "time",        resp_time },
    { "uptime",      resp_uptime },
    { "status_page", resp_status_page },
};

static char * query_lookup(char *query, char *name)
{
    char *ptr = query;
    char *item = NULL;
    char *name_start, *name_end;
    int name_len;

    if (!query || !name)
        return NULL;

    name_len = strlen(name);

    do {
        name_start = strstr(ptr, name);
        if (name_start) {
            ptr = name_start + 1;
            if (name_start[name_len] == '=') {
                name_start += name_len + 1;
                name_end = strchr(name_start, '&');
                if (name_end == NULL)  {
                    name_end = strchr(name_start, '\0');
                }
                item = calloc(name_end - name_start + 1, sizeof(char));
                strncpy(item, name_start, name_end - name_start);
                break;
            }
        }
    } while(name_start);

    return item;
}

static void handle_request(void)
{
    char *method = getenv("REQUEST_METHOD");
    char *item = query_lookup(getenv("QUERY_STRING"), "item");
    int handled = FALSE;
    int i;

    if (!strcmp(method, "GET")) {
        for (i = 0; i < ARRAY_SIZE(item_handlers); i++) {
            if (item && !strcmp(item, item_handlers[i].name)) {
                item_handlers[i].fnPtr();
                handled = TRUE;
                break;
            }
        }
        if (!handled)
            resp_invalid_request(404, "Invalid item");
    }
    else {
        resp_invalid_request(405, "Only GET Method Allowed");
    }

    if (item)
        free(item);
}

int main(int argc, char **argv)
{
    initialize();

    while (FCGI_Accept() >= 0) {
        handle_request();
    }

    return 0;
}
