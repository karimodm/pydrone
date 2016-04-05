/* FROM "Router Trapper" to Traffic Dumper FOR PYTHON!!! by karimo */

#ifdef MY__PYTHON
#	include <Python.h>
#	define RETURN { Py_INCREF(Py_None); return Py_None; }
#else
#	define RETURN
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pcap.h>
#ifndef PCAP_SRC_IF_STRING
#	define PCAP_SRC_IF_STRING "rpcap://"
#endif
#ifdef _UNIX
#	include <pthread.h>
#elif defined(WIN32)
#	include <windows.h>
#else
#	error NO_OPERATING_SYSTEM_DEFINED
#endif

#ifdef _UNIX
static pthread_t t;
#else
#error NOT_IMPLEMENTED
#endif
static pcap_t *cap;

static void handle_pkt(u_char *dumper,const struct pcap_pkthdr *head,const u_char *data) {
	pcap_dump(dumper,head,data);
}

/* Receives only one argument: the ASCII filter in pcap format */
static void __start_hook(char *u_filter) {
	if (cap) return;
	char buf[PCAP_ERRBUF_SIZE],aux[64],tmp[16],*dev;
	struct bpf_program filter;
	pcap_dumper_t *dumpfile;
	/* Monitor default device */
	dev=pcap_lookupdev(buf);
	if (!dev) return;
	cap=(pcap_t *)pcap_open_live(dev,0xFFFF,0,0,buf);
	if (cap) {
		pcap_compile(cap,&filter,u_filter,0,0);
		pcap_setfilter(cap,&filter);
		memset(aux,0,64);
		sprintf(tmp,"%d\0",(int)time(NULL));
		dumpfile=pcap_dump_open(cap,strcat(strcat(strcat(aux,"hook_\0"),tmp),".cap\0"));
		pcap_loop(cap,0,handle_pkt,(u_char *)dumpfile);
	}
}

#ifdef MY__PYTHON
/* Python-Only Function */
static PyObject *start_hook(PyObject *self,PyObject *args) {
	char *u_filter;
	PyArg_ParseTuple(args,"s",&u_filter);
#ifdef _UNIX
	pthread_create(&t,NULL,(void *(*)(void *))&__start_hook,(void *)u_filter);
#else
#error NOT_IMPLEMENTED
#endif
	RETURN;
}
#endif

#ifdef MY__PYTHON
static PyObject *stop_hook(PyObject *self,PyObject *args)
#else
void stop_hook()
#endif
{
/* If not MY__PYTHON doesn't use threads */
#ifdef MY__PYTHON
#ifdef _UNIX
	pthread_cancel(t);
#else
#error NOT_IMPLEMENTED
#endif
#endif /* MY__PYTHON */
	if (cap) {
	    pcap_close(cap);
	    cap=NULL;
	}
	RETURN;
}

#ifdef MY__PYTHON
static PyMethodDef HookFunctions[]={
	{"start_hook",start_hook,METH_VARARGS,"Set the Hook with Filter."},
	{"stop_hook",stop_hook,METH_VARARGS,"Stop the Hook."},
	{NULL, NULL, 0, NULL} /* Sentinel */
};

PyMODINIT_FUNC inithooktraffic() {
	cap=NULL;
	Py_InitModule("hooktraffic",HookFunctions);
}
#else
int main(int argc,char **argv) {
  if (argc<2) exit(-1);
  cap=NULL;
  __start_hook(argv[1]);
}
#endif
