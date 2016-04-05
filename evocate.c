#include <Python.h>
#include <string.h>

int main(int argc,char **argv) {
	int j,restart;
	char pypath[512];
	PyObject *mod,*initfunc;
	for (j=strlen(argv[0])-1;j>=0;j--)
	    if (argv[0][j]=='/' || argv[0][j]=='\\') {
		argv[0][j+1]='\0';
		break;
	    }
	do {
	    memset(pypath,0,512);
	    Py_Initialize();
	    strcat(strcat(strcat(pypath,Py_GetPath()),":\0"),argv[0]);
	    PySys_SetPath(pypath);
	    mod=PyImport_ImportModule("init");
	    initfunc=PyDict_GetItemString(PyModule_GetDict(mod),"initialize_drone");
	    restart=PyInt_AsLong(PyObject_CallObject(initfunc,NULL));
	    Py_Finalize();
	} while (restart==1);
	/* Se restart == 0 non fa un cazzo, se è ==2 si eradica */
	if (restart==2) { /* TODO: ERADICATE */ }
}
