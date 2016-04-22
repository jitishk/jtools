#!/bin/bash
# This script is a hack to workaround the blocking nature of 'ssr-sim start',
# it terminates in a strange way which makes the python script hang, hence this proxy
$1 start $2 1>/dev/null 2>/dev/null