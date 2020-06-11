# wol
wake on lan and some useful stuff as web service.

## install

```bash
pip install poetry
poetry install
```

## launch

```bash
poetry run python main.py
```

to get command-line arguments type `poetry run python main.py -h`.  
default listen address - `127.0.0.1:5000`.

## usage

**api**  
`*` - required parameter,  
body and response format - json.

`POST /api/check_host/` - check, if host online.  
body parameters:
* *`host` - (*string*) ip address or hostname of remote host.

example:
  ```json
  {
    "host": "192.168.1.25"
  }
  ```

response fields:
* `reached` - (*bool*) is a remote host online.

`POST /api/wake/` - wakeup host by Wale on lan.  
body parameters:
* *`mac` - (*string*) mac address of remote host;
* `ip_address` - (*string*) remote host address. default - `"255.255.255.255"`;
* `port` - (*int*) wake on lan port. default - 9.

example:
  ```json
  {
    "mac": "01:23:45:67:ab:CD",
    "ip_address": "255.255.255.255",
    "port": 9
  }
  ```

`POST /api/cpu_stat/` - cpu load of remote host (ssh)
http://www.linuxhowtos.org/manpages/5/proc.htm.  
body parameters:
* *`host` - (*string*) ip address or hostname of remote host;
* `port` - (*int*) ssh port. default - 22;
* *`login` - (*string*) ssh login;
* *`password` - (*string*) ssh password.

example:
  ```json
  {
    "host": "192.168.1.25",
    "login": "user",
    "password": "WeRySeCrEtPaSsWoRd"
  }
  ```

response fields:
* `user` - (*number*) time spent in user mode;
* `nice` - (*number*) time spent in user mode with low priority (nice);
* `system` - (*number*) time spent in system mode;
* `idle` - (*number*) time spent in the idle task;
* `iowait` - (*number*) time waiting for I/O to complete;
* `irq` - (*number*) time servicing interrupts;
* `softirq` - (*number*) time servicing softirqs;
* `steal` - (*number*) stolen time, which is the time spent in other operating systems when running in a virtualized environment;
* `guest` - (*number*) time spent running a virtual CPU for guest operating systems under the control of the Linux kernel;
* `guest_nice` - (*number*) time spent running a niced guest.

`POST /api/scan_net/` - search all hosts in local net.  
response fields:
* `hosts` - (*array[string]*) - list of hosts ip addresses.

`POST /api/reboot/` - reboot a remote host (ssh).  
body parameters:
* *`host` - (*string*) ip address or hostname of remote host;
* `port` - (*int*) ssh port. default - 22;
* *`login` - (*string*) ssh login;
* *`password` - (*string*) ssh password.

example:
  ```json
  {
    "host": "192.168.1.25",
    "login": "user",
    "password": "WeRySeCrEtPaSsWoRd"
  }
  ```

---

## todo

* local store
  * hosts and their credentials
* ssh pkey
* access control
* openapi doc
* docker?
* extend functionality
* browsable interface
* tests
