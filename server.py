import socket
import threading
import time
import errno
import sys


def get_error_name(e):
    if e == errno.EPERM:
        return 'Operation not permitted'
    if e == errno.ENOENT:
        return 'No such file or directory'
    if e == errno.ESRCH:
        return 'No such process'
    if e == errno.EINTR:
        return 'Interrupted system call'
    if e == errno.EIO:
        return 'I/O error'
    if e == errno.ENXIO:
        return 'No such device or address'
    if e == errno.E2BIG:
        return 'Arg list too long'
    if e == errno.ENOEXEC:
        return 'Exec format error'
    if e == errno.EBADF:
        return 'Bad file number'
    if e == errno.ECHILD:
        return 'No child processes'
    if e == errno.EAGAIN:
        return 'Try again'
    if e == errno.ENOMEM:
        return 'Out of memory'
    if e == errno.EACCES:
        return 'Permission denied'
    if e == errno.EFAULT:
        return 'Bad address'
    if e == errno.EBUSY:
        return 'Device or resource busy'
    if e == errno.EEXIST:
        return 'File exists'
    if e == errno.EXDEV:
        return 'Cross-device link'
    if e == errno.ENODEV:
        return 'No such device'
    if e == errno.ENOTDIR:
        return 'Not a directory'
    if e == errno.EISDIR:
        return 'Is a directory'
    if e == errno.EINVAL:
        return 'Invalid argument'
    if e == errno.ENFILE:
        return 'File table overflow'
    if e == errno.EMFILE:
        return 'Too many open files'
    if e == errno.ENOTTY:
        return 'Not a typewriter'
    if e == errno.ETXTBSY:
        return 'Text file busy'
    if e == errno.EFBIG:
        return 'File too large'
    if e == errno.ENOSPC:
        return 'No space left on device'
    if e == errno.ESPIPE:
        return 'Illegal seek'
    if e == errno.EROFS:
        return 'Read-only file system'
    if e == errno.EMLINK:
        return 'Too many links'
    if e == errno.EPIPE:
        return 'Broken pipe'
    if e == errno.EDOM:
        return 'Math argument out of domain of func'
    if e == errno.ERANGE:
        return 'Math result not representable'
    if e == errno.EDEADLK:
        return 'Resource deadlock would occur'
    if e == errno.ENAMETOOLONG:
        return 'File name too long'
    if e == errno.ENOLCK:
        return 'No record locks available'
    if e == errno.ENOSYS:
        return 'Function not implemented'
    if e == errno.ENOTEMPTY:
        return 'Directory not empty'
    if e == errno.ELOOP:
        return 'Too many symbolic links encountered'
    if e == errno.EWOULDBLOCK:
        return 'Operation would block'
    if e == errno.ENOMSG:
        return 'No message of desired type'
    if e == errno.EIDRM:
        return 'Identifier removed'
    if e == errno.EDEADLOCK:
        return 'File locking deadlock error'
    if e == errno.ENOSTR:
        return 'Device not a stream'
    if e == errno.ENODATA:
        return 'No data available'
    if e == errno.ETIME:
        return 'Timer expired'
    if e == errno.ENOSR:
        return 'Out of streams resources'
    if e == errno.EREMOTE:
        return 'Object is remote'
    if e == errno.ENOLINK:
        return 'Link has been severed'
    if e == errno.EPROTO:
        return 'Protocol error'
    if e == errno.EBADMSG:
        return 'Not a data message'
    if e == errno.EOVERFLOW:
        return 'Value too large for defined data type'
    if e == errno.EILSEQ:
        return 'Illegal byte sequence'
    if e == errno.EUSERS:
        return 'Too many users'
    if e == errno.ENOTSOCK:
        return 'Socket operation on non-socket'
    if e == errno.EDESTADDRREQ:
        return 'Destination address required'
    if e == errno.EMSGSIZE:
        return 'Message too long'
    if e == errno.EPROTOTYPE:
        return 'Protocol wrong type for socket'
    if e == errno.ENOPROTOOPT:
        return 'Protocol not available'
    if e == errno.EPROTONOSUPPORT:
        return 'Protocol not supported'
    if e == errno.ESOCKTNOSUPPORT:
        return 'Socket type not supported'
    if e == errno.EOPNOTSUPP:
        return 'Operation not supported on transport endpoint'
    if e == errno.EPFNOSUPPORT:
        return 'Protocol family not supported'
    if e == errno.EAFNOSUPPORT:
        return 'Address family not supported by protocol'
    if e == errno.EADDRINUSE:
        return 'Address already in use'
    if e == errno.EADDRNOTAVAIL:
        return 'Cannot assign requested address'
    if e == errno.ENETDOWN:
        return 'Network is down'
    if e == errno.ENETUNREACH:
        return 'Network is unreachable'
    if e == errno.ENETRESET:
        return 'Network dropped connection because of reset'
    if e == errno.ECONNABORTED:
        return 'Software caused connection abort'
    if e == errno.ECONNRESET:
        return 'Connection reset by peer'
    if e == errno.ENOBUFS:
        return 'No buffer space available'
    if e == errno.EISCONN:
        return 'Transport endpoint is already connected'
    if e == errno.ENOTCONN:
        return 'Transport endpoint is not connected'
    if e == errno.ESHUTDOWN:
        return 'Cannot send after transport endpoint shutdown'
    if e == errno.ETOOMANYREFS:
        return 'Too many references: cannot splice'
    if e == errno.ETIMEDOUT:
        return 'Connection timed out'
    if e == errno.ECONNREFUSED:
        return 'Connection refused'
    if e == errno.EHOSTDOWN:
        return 'Host is down'
    if e == errno.EHOSTUNREACH:
        return 'No route to host'
    if e == errno.EALREADY:
        return 'Operation already in progress'
    if e == errno.EINPROGRESS:
        return 'Operation now in progress'
    if e == errno.ESTALE:
        return 'Stale NFS file handle'
    if e == errno.EDQUOT:
        return 'Quota exceeded'
    return "Unknown"


class API:
    def __init__(self, callback):
        self.receive_thread = threading.Thread(target=self.receive_loop)
        self.done = False
        self.callback = callback
        self.receive_thread.start()
        time.sleep(0.5)

    def shutdown(self):
        self.done=True
        time.sleep(0.1)

    def receive_loop(self):
        from pyrobsim import DEBUG
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind(('127.0.0.1', 9080))
            sock.setblocking(0)
        except OSError as e:
            self.done=True
            print("Failed to bind socket")
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while not self.done:
            try:
                data, address = sock.recvfrom(256)
                if len(data) == 0:
                    time.sleep(0.01)
                else:
                    words = str(data,encoding='utf-8').strip().split()
                    if DEBUG:
                        print("Received from '{}' data='{}'".format(address, data))
                    if len(words) < 1:
                        continue
                    try:
                        cmd = words[0]
                        args = [float(a) for a in words[1:]]
                        response = self.callback(cmd, args)
                        if len(response)>0:
                            send_sock.sendto(bytes(response,'utf-8'),(address[0],9081))
                    except ValueError:
                        pass
            except OSError as e:
                error_number = e.errno
                if error_number != errno.EAGAIN  and error_number != errno.EWOULDBLOCK:
                    reason = get_error_name(error_number)
                    print("Socket Error ({}): {}".format(error_number, reason))
        sock.close()
        send_sock.close()
