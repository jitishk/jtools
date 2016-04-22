#
# 05/07/2012
#
#    Copyright (c) 2012 Ericsson AB.
#    All rights reserved.
#

"""
   This module is used to debug packet forwarding path on SSR
   for the ping functionality.
"""

import sys
import decimal
import operator
import string
import re
from SSR.SWRP.cli import hltp_exec_cli
from SSR.SWRP.cli.hltp_show_context import *
from SSR.SWRP.cli.hltp_show_ip_route import *
from SSR.SWRP.cli.hltp_show_card import *
from generic.actions.hltp_gen_TS import *


#
# This is a wrapper for hltp_ping_debug() to invoke the function in the
# troubleshoot thread context
#
def healthd_ping_debug(dest_ip, context):
    """
       Debug ping failure to a particular ip address (Troubleshoot thread)

       Input:
           dest_ip: Destination ip address to check.
           context: Context to check

       Returns:
           True: if no errors found.
           False: if errors found. 

       Usage:
           healthd_ping_debug(dest_ip, context):
           e.g. healthd_ping_debug('10.1.1.1', 'local' ) will debug
           ping failure for ip address 10.1.1.1 in context local and display
           if there are any errors. 
    """
    temp_cmd = ["hltp_ping_debug('", dest_ip, "', '", context, "')"]
    healthd_troubleshoot("".join(temp_cmd))

def rib_collect_logs():
    # Spawn exec_cli
    print("\nSpawning Interactive console: ", end=' ')
    exec_cli = hltp_exec_cli.hltp_exec_cli_object()
    if exec_cli.is_ready() == False:
        print("FAIL - Could not get CLI prompt")
        return False
    else:
        print("OK")
    context = 'local'
    exec_cli.sendline('context ' + context)
    exec_cli.expect_prompt()
    # Issue a show ip route command for dest_ip
    exec_cli.sendline('show ip route all')
    exec_cli.expect_prompt()
    temp_buffer = exec_cli.before
    print temp_buffer
#
# Function to debug ping failure.
#
def hltp_ping_debug(dest_ip, context):
    """
       Debug ping failure to a particular ip address.

       Input:
           dest_ip: Destination ip address to check.
           context: Context to check

       Returns:
           True: if no errors found.
           False: if errors found. 

       Usage:
           hltp_ping_debug( dest_ip, context ):
           e.g. hltp_ping_debug( '10.1.1.1', 'local' ) will debug
           ping failure for ip address 10.1.1.1 in context local and display
           if there are any errors. 
    """

    # Spawn exec_cli
    print("\nSpawning Interactive console: ", end=' ')
    exec_cli = hltp_exec_cli.hltp_exec_cli_object()
    if exec_cli.is_ready() == False:
        print("FAIL - Could not get CLI prompt")
        return False
    else:
        print("OK")
    
    # validate the ip address
    print("Verifying IP address '", dest_ip, "' : ", end=' ')
    if hltp_validate_ipv4_addr(dest_ip) == True:
        print("OK")
    else:
        print("FAIL - Invalid Destination IP Address ")
        return False

    # Validate context
    print("Verifying context '", context, "' : ", end=' ')
    if hltp_verify_context(exec_cli, context) == True:
        print("OK")
    else:
       print("FAIL - Invalid context")
       return False

    # Change to that particular context
    try:
        exec_cli.sendline('context ' + context)
        exec_cli.expect_prompt()
    except:
        print("FAIL - Could not interact with CLI")
        return False
    
    # Get the 'show ip route dest_ip details'
    print("Verifying RIB route: 'show ip route ", dest_ip, " detail' : ", end=' ')
    (err, ip_list) = hltp_show_ip_route_ip_detail(exec_cli, dest_ip)
    if err is False:
        print("FAIL - No route in RIB")
        return False

    print("OK")
    print('   matched route                 : ', ip_list['route_match']) 
    print('   matched route type            : ', ip_list['found'])
    print('   route in kernel               : ', ip_list['route_kernel'])
    print('   Next Hop ID                   : ', ip_list['next_hop_id']) 
    print('   Adjacency ID                  : ', ip_list['adj_id'])
    print('   Circuit                       : ', ip_list['circuit'])
    print('   Route Downloaded to the slots : ', ip_list['ippa_slots'])
    print('   Interface                     : ', ip_list['interface'])

    # Right now we support only two interface types starting with 0x311
    # and 0x345. For all other interface types we just stop and return.
    if ip_list['next_hop_id'].startswith(('0x311','0x345')) == False:
        print('FAIL - Use case not supported for this next hop interface')
        return False
    
    # Get the 'show ip route next_hop_id details'
    print("Verifying RIB nexthop: 'show ip route next-hop ", ip_list['next_hop_id'], " detail' : ", end=' ')
    (err, nh_ip_list) = hltp_show_ip_route_nexthop_detail(exec_cli, ip_list['next_hop_id']) 
    if err is False:
        print("FAIL - No nexthop in RIB")
        return False
    
    print("OK")
    print('   Adjacency ID               : ', nh_ip_list['nh_adj_id'])
    if (nh_ip_list['nh_conn'] != 'Yes'):
        print('   NH Connected               : *** NO ***')
    else:
        print('   NH Connected               : ', nh_ip_list['nh_conn'])
    print('   Interface                  : ', nh_ip_list['nh_interface'])
    print('   Interface grid ID          : ', nh_ip_list['nh_if_grid'])
    print('   iPPA                       : ', nh_ip_list['nh_ippa'])
    print('   ePPA                       : ', nh_ip_list['nh_eppa'])
   
    # if adj id is None, then return.
    if (ip_list['adj_id'] is None) or (nh_ip_list['nh_adj_id'] is None):
        print("FAIL - Adjacency ID is not set.")
        return False
         
    print("Verifying RIB ip route and nexthop adjacency : ", end=' ')
    if int(ip_list['adj_id'],0) != int(nh_ip_list['nh_adj_id'], 0):
        print("FAIL - RIB route and nexthop adj mismatch")
        return False
    else :
        print("OK")
    
    print("Verifying RIB ip route and nexthop interface : ", end=' ')
    if ip_list['interface'] != nh_ip_list['nh_interface']:
        print("FAIL - RIB route and nexthop interface mismatch")
        return False
    else :
        print("OK")
   
    # if slot number is None, then return. 
    if (ip_list['ippa_slots'] is None) or (nh_ip_list['nh_ippa'] is None): 
        print("FAIL - Slot number is not set.")
        return False

    print("Verifying RIB ip route and nexthop slots : ", end=' ')
    if int(ip_list['ippa_slots']) != int(nh_ip_list['nh_ippa']):
        print("FAIL - RIB route and nexthop slots mismatch")
        return False
    else :
        print("OK")

    # Connected nexthops
    if (nh_ip_list['nh_conn'] == 'Yes'):
        # Check for ARP entry in RIB
        arp_route = "".join(dest_ip + "/32")
        print("Verifying connected route matches /32 : ", end=' ')
        if ip_list['route_match'] != arp_route:
            print("FAIL - No ARP route in RIB")
            return False
    
    # Get FIB entries from iPPA
    print("Verifying FIB entries on iPPAs : 'show card x fabl fib nexthop ", ip_list['next_hop_id'], " detail' : ", end=' ')
    slot_cards = ip_list['ippa_slots'].split()
    for each_slot in slot_cards: 
        (err, ifib) = hltp_show_card_fabl_fib_nh_id(exec_cli, str(each_slot), str(ip_list['next_hop_id']))
        if err is False:
            print("FAIL - could not get show card fabl")
            return False
        else:
            print("OK")
        print("     INGRESS-FIB details for slot %s:" %(each_slot)) 
        print("     Destination Slot : ",ifib['dstslot'])
        print("     State            : ",ifib['state'])
        print("     Context          : ",ifib['context'])
        print("     NextHopType      : ",ifib['nexthoptype'])
        print("     Circuit          : ",ifib['ifib_circuit'])
        print("     Adjacency        : ",ifib['adjacency'])
        print("     Flags            : ",ifib['flags'])
        print("     RefCount         : ",ifib['ref_count'])
        print("     RibVersion       : ",ifib['rib_version'])
        print("     FibVersion       : ",ifib['fib_version'])
        print("     IP               : ",ifib['ip'])
        print("     CNH-Type         : ",ifib['cnh_type'])
        print("     DstCookie        : ",ifib['dstcookie'])
        print("     AdjCookie        : ",ifib['adjcookie'])
        print("     AldVersion       : ",ifib['aldversion'])
        print("     FeatureBitmask   : ",ifib['featurebitmask'])
    return True

#
#
#
def hltp_validate_ipv4_addr(ip):
    """
        Validates IPv4 addresses.
    """
    
    pattern = re.compile(r"""
        ^
        (?:
          # Dotted variants:
          (?:
            # Decimal 1-255 (no leading 0's)
            [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
          |
            0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
          |
            0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
          )
          (?:                  # Repeat 0-3 times, separated by a dot
            \.
            (?:
              [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
            |
              0x0*[0-9a-f]{1,2}
            |
              0+[1-3]?[0-7]{0,2}
            )
          ){0,3}
        |
          0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
        |
          0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
        |
          # Decimal notation, 1-4294967295:
          429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
          42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
          4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
        )
        $
    """, re.VERBOSE | re.IGNORECASE)
    return pattern.match(ip) is not None



