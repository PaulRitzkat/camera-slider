#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from time import sleep
from tinkerforge.ip_connection import IPConnection
from tinkerforge.brick_red import RED

def check_error(error_code, *args):
    if error_code != 0:
        print('RED Brick error occurred: {0}'.format(error_code))
        sys.exit(1)

    if len(args) == 1:
        return args[0]

    return args

def start_program(red, identifier):
    session_id = check_error(*red.create_session(30))
    program_list_id = check_error(*red.get_programs(session_id))
    started = False

    for i in range(check_error(*red.get_list_length(program_list_id))):
        program_id, _ = check_error(*red.get_list_item(program_list_id, i, session_id))

        string_id = check_error(*red.get_program_identifier(program_id, session_id))
        string_length = check_error(*red.get_string_length(string_id))
        string_data = ''

        while len(string_data) < string_length:
            string_data += check_error(*red.get_string_chunk(string_id, len(string_data)))

        check_error(red.release_object(string_id, session_id))

        if string_data.decode('utf-8') == identifier:
            check_error(red.start_program(program_id))
            started = True

        check_error(red.release_object(program_id, session_id))

        if started:
            break

    check_error(red.release_object(program_list_id, session_id))
    check_error(red.expire_session(session_id))

    return started

if __name__ == '__main__':
    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
        uid = sys.argv[3]
        identifier = sys.argv[4]
        wait = int(sys.argv[5])
    except:
        print('usage: {0} <host> <port> <red-uid> <program-identifier> <wait-duration>'.format(sys.argv[0]))
        sys.exit(1)

    ipcon = IPConnection()
    red = RED(uid, ipcon)

    ipcon.connect(host, port)

    if start_program(red, identifier):
        sleep(wait / 1000.0)

    ipcon.disconnect()

    if not started:
        print('RED Brick program not found: {0}'.format(identifier))
        sys.exit(2)
