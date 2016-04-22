

void
urib_add_address (uint32_t context_id, uint32_t proto_id, prefix_t* prefix, nexthop_t* in_nexthop) {
    path_t * path;
    address_t *   address;
    address = urib_global_db_locate_address(context_id, proto_id, address->prefix);
    path = urib_global_db_locate_path(context_id, proto_id, in_path->ip, in_path->cct);

    
    urib_address_link_path(address, path);

    clients_list_t * list;
    list = urib_global_db_findall_redistribution_destination_clients(context_id, proto_id);
    client_t * client;
    for (client = urib_client_list_get_first(list); client != NULL; client = urib_client_list_get_next(list, client)) {
        urib_client_send_redistribution(client, address, path);
    }
    list = urib_global_db_findall_reachability_query_clients(context_id, address->prefix);
    for (client = urib_client_list_get_first(list); client != NULL; client = urib_client_list_get_next(list, client)) {
        urib_client_send_rechability_response(client, address, path);
    }
}

void
urib_delete_route (uint32_t context_id, uint32_t proto_id, route_t* in_route, nexthop_t* in_nexthop) {
    nexthop_t * nexthop;
    route_t *   route;
    route = urib_global_db_find_route(context_id, proto_id, route->prefix);
    nexthop = urib_global_db_find_nexthop(context_id, proto_id, in_nexthop->ip, in_nexthop->cct);

    if (route && nexthop && urib_route_islinked_path(route, nexthop)) {
        urib_route_unlink_path(route, nexthop);
        if (urib_route_can_be_removed(route)) {
            urib_global_db_remove_route(route);
        }
        if (urib_nexthop_can_be_removed(nexthop)) {
            urib_global_db_remove_nexthop(nexthop);
        }

        list_t * list;
        list = urib_global_db_findall_redistribution_destination_clients(context_id, proto_id);
        client_t * client;
        for (client = urib_client_list_get_first(list); client != NULL; client = urib_client_list_get_next(list, client)) {
            urib_client_send_redistribution(client, route, nexthop);
        } 
        list = urib_global_db_findall_reachability_query_clients(context_id, route->prefix);
        for (client = urib_client_list_get_first(list); client != NULL; client = urib_client_list_get_next(list, client)) {
            urib_client_send_rechability_response(client, route, nexthop);
        }
        list = urib_global_db_findall_downloaded_slots(context_id, route->prefix);
        for (slot = urib_slot_list_get_first(list); slot != NULL; slot = urib_slot_list_get_next(list, slot)) {
            urib_client_send_rechability_response(slot, route, nexthop);
        }
    }
} 

void
urib_add_client (uint32_t context_id, uint32_t client_type, const char* client_instance, uint32_t *proto_id_p) {

    client_t* client;
    client = urib_global_db_get_client(context_id, client_type, client_instance);

    if (!client) {
        urib_client_allocate(&client);
        urib_client_initialize(client, proto_id, client_type, client_instance);
        urib_client_do_registration_stuff(client);
        urib_global_db_add_client(client);
    } else {
    }
    *proto_id_p = client->proto_id;
} 
 
void
urib_delete_client (uint32_t context_id, uint32_t proto_id) {

    /* Get an already registered client, if any */
    client_t* client;
    client = urib_global_db_get_client(context_id, proto_id);

    if (client) {
        urib_client_do_deregistration_stuff(client);
        urib_client_deinitialize(client);
        urib_global_db_remove_client(client);
        urib_client_deallocate(&client);
    } else {
        //Handle client state machine
    }
} 

void
urib_add_context (uint32_t context_id) {
    context_t * context;
    context = urib_global_db_find_context(context_id);
    if (!context) {
        urib_context_allocate(&context);
        urib_context_init(context, context_id);
        urib_global_db_insert_context(context->id, context);
    } else {
        //Handle recreation of context
    }
}
 
void
urib_delete_context (uint32_t context_id) {
    context_t * context;
    context = urib_global_db_find_context(context_id);
    if (context) {
        urib_context_cleanup(context);
        urib_global_db_remove_context(context->id, context);
        urib_context_deallocate(&context);
    } else {
        //Handle recreation of context
    }
}

 
