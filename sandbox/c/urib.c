#include <stdio.h>

uint32_t urib_get_next_proto_id() {
    static last_proto_id = 1;
    return last_proto_id++;
}

typedef struct _hook_t {
    struct _hook_t* next;
    struct _hook_t* prev;
} hook_t, list_t;

typedef struct {
    //change to hook with key
    hook_t      nexthop_db_hook;
    uint32_t    nexthop_id;
} nexthop_t;

typedef struct {
    //Change to hook with key
    hook_t      path_db_hook;
    uint32_t    proto_id;

    list_t      client_added_paths_list_hook;
    list_t      routes_dependency_list;
    nexthop_t   nexthop;
} path_t;

typedef struct {
    list_t  adjacency_list;
    list_t  lsp_list;
    list_t  ip_list;
} paths_db_t;

typedef struct {
    list_t  rrqs_list;
} rrqs_db_t;

typedef struct {
    list_t redistributions_list;
} redistributions_db_t;

typedef struct {
    hook_t      nexthop_routes_dependency_list_hook;
    hook_t      context_routes_deallocate_list_hook;

    //change to hook with key
    hook_t      context_routes_db_hook; 
    uint32_t    prefix;
    uint32_t    prefix_len;

    paths_db_t  paths_db;
    rrq_db_t    rrq_db;
    redistributions_db_t    redistributions_db;
    uint32_t    downloaded_slots;
}route_t;

typedef struct {
    hook_t client_transmissions_list_hook;
    void *msg;
} transmission_t;

typedef struct {
    route_t routes[100];
} routes_db_t;
typedef struct {
    nexthop_t   nexthops[100];
} nexthops_db_t;

typedef struct {
    //May need a key, if # of redistribute requesting clients are large.
    list_t redistribution_destination_clients_list;
} redistribution_destination_clients_db_t;

typedef struct {
    //TODO: change to a hook with key
    hook_t                                      context_clients_db_hook;
    uint32_t                                    proto_id;
    hook_t                                      context_client_type_db_hook;
    char                                        instance[50];

    hook_t                                      client_redistribution_destination_clients_db_hook;
    hook_t                                      context_client_deallocate_list_hook;

    redistribution_destination_clients_db_t     redistribution_destination_clients_db;
    transmissions_db_t                          transmissions_db;
    client_added_paths_db_t                     client_added_paths_db;
}client_t;
void
urib_client_allocate (client ** client_pp) {
    *client_pp = (client_t *) malloc (sizeof(client_t));
}
urib_client_initialize (client * client, uint32_t proto_id, uint32_t client_type, const char * client_instance) {
    memset(client, 0, sizeof (client));
    client->proto_id = proto_id;
    client->client_type = client_type;
    strncpy(client->instance, client_instance, sizeof (client->instance));
    urib_redistribution_clients_db_initialize(&(client->redistribution_destination_clients_db));
    urib_transmissions_db_intialize(&(client->transmissions_db));
    urib_client_added_paths_db_intialize(&(client->transmissions_db));
}
void
urib_client_cleanup (client_t* client) {
    context_t * context = urib_global_db_get_context(client->context_id);
    urib_client_redistribution_destination_clients_cleanup(client->redistribution_destination_clients_db);
    urib_client_added_paths_cleanup(client->client_added_paths_list);
    urib_client_transmissions_cleanup(client->transmissions_list);

    urib_client_context_clients_db_unhook(client, context);
    urib_client_context_client_type_db_unhook(client, context);
    urib_client_redistribution_destination_clients_db_unhook(client, context);
}
void
urib_client_do_registration_stuff(client_t * client) {
}
 

 



typedef struct {
    client_t    client[100];
} clients_db_t;

typedef struct {
    routes_db_t         routes_db;
    clients_db_t        clients_db;
    nexthops_db_t       nexthops_db;
    client_types_db_t   client_types_db;
    
    list_t              clients_dealloc_list;
} context_t;
typedef struct {
    context_t   contexts[100];
} contexts_db_t;
 
typedef struct {
    list_t* client_types[CLIENT_TYPES];
} client_types_db_t;


client_t *
urib_client_types_db_get_client (client_types_db_t* client_types_db, uint32_t client_type,
        const char * client_instance) {
    client_t client = client_types_db->client_types[client_type]->next;
    while (client) {
        if (strncmp(client->client_instance, client_instance, sizeof(client->client_instance)) == 0) {
            return client;
        }
        client = clients_list->next;
    }
}

client_t *
urib_context_get_client (const context_t* context, uint32_t client_type, const char * client_instance) {
    return urib_client_types_db_get_client(context->client_types_db, client_type, client_instance);
}

void
urib_context_add_client(context_t * context, client_t * client) {
    urib_clients_db_insert_client(context->clients_db, client);
    //insert into client list indexed by proto id
    //insert into client list indexed by client type and instance
}


void
urib_client_redistribution_destination_clients_cleanup(redistribution_destination_clients_db_t redistribution_destination_clients_db) {
    list_t client_list = redistribution_destination_clients_db->redistribution_destiation_clients_list;
    client_t * client = redistribution_destination_clients_db->redistribution_destination_clients_list->next;
    while (client) {
        urib_client_unhook(client, URIB_CLIENT_REDISTRIBUTION_CLIENT_LIST);
    }
}
void
urib_client_added_paths_cleanup(list_t client_added_paths_list) {
    path_t * path = list->next;
    while (path) {
        urib_path_cleanup(path);
    }
}
void
urib_client_transmissions_cleanup(list_t transmissions_list) {
    transmission_t * transmission = transmissions_list->next;
    while(transmission) {
        urib_transmission_dealloc(transmission);
        transmission = transmission->list;
    }    
}



void
urib_clients_db_cleanup (clients_db_t * clients_db) {
    for (i=0; i<100; i++) {
        client_t * client = clients_db->clients[i];
        if (client) {
            urib_client_cleanup(client);
        }
    }
}

void
urib_global_db_get_client (uint32_t context_id, uint32_t client_type, const char * client_instance) {
    /* Depending on how the global db is structured, this is redefined */
    context_t * context = urib_global_db_get_context (context_id);
    clients_db_t * clients_db = urib_context_get_client_db(context);
    return urib_clients_db_get_client(clients_db, client_type, client_instance);
}
void
urib_global_db_get_client (uint32_t context_id, uint32_t proto_id) {
    /* Depending on how the global db is structured, this is redefined */
    context_t * context = urib_global_db_get_context (context_id);
    clients_db_t * clients_db = urib_context_get_client_db(context);
    return urib_clients_db_get_client(clients_db, proto_id);
}
void
urib_global_db_add_client (client_t * client) 
{
    /* Depending on how the global db is structured, this is redefined */
    context_t * context = urib_global_db_get_context (client->context_id);
    clients_db_t * clients_db = urib_context_get_client_db(context);
    urib_clients_db_add_client(clients_db, client);
}
