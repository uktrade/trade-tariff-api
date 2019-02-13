import io
import os
import sys
import logging

from ftplib import FTP
from ftplib import FTP_TLS
from ftplib import all_errors

from apifiles3 import get_file_list
from apifiles3 import get_file
from apifiles3 import write_file
from apifiles3 import rename_file


class MyFTP_TLS(FTP_TLS):
    """Explicit FTPS, with shared TLS session"""
    def ntransfercmd(self, cmd, rest=None):
        conn, size = FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,
                                            server_hostname=self.host,
                                            session=self.sock.session)  # this is the fix
        return conn, size


FTPHOST = os.environ.get("FTPHOST")
FTPPORT = int(os.environ.get("FTPPORT"))
FTPUSER = os.environ.get("FTPUSER")
FTPPASSWORD = os.environ.get("FTPPASSWORD")
FTPUSERROOT = os.environ.get("FTPUSERROOT", "/")

# Define logging for debugging
logger = logging.getLogger('ftps3client')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def s3_to_ftps(folder):
    logger.info('s3_to_ftps: ' + folder)
    try:
        ftp.cwd(FTPUSERROOT + folder)
        s3files = get_file_list(folder)
        for file in s3files:
            f = file['Key']
            fn = f[f.rindex("/")+1:]                        # remove folder prefix
            if (fn != "" and not '/success/' in f):         # ignore object that is just the folder name
                                                            # and already processed files
                logger.info("Uploading file " + f)

                ftp.storbinary('STOR ' + fn, get_file(f))   # get_file gives us the readable stream

                print(f + " ----- " + folder + '/success/' + fn)
                rename_file(f, folder + '/success/' + fn)   # in s3

    except all_errors as e:
        logger.exception(e)


def ftps_to_s3(folder):
    logger.info('ftps_to_s3: ' + folder)

    try:
        ftp.cwd(FTPUSERROOT + folder)
        logger.info('Changed directory to ' + ftp.pwd())

        dirlines = []
        ftp.retrlines('LIST', dirlines.append)

        for d in dirlines:
            if (d[0] != "d"):               # d indicates directory
                logger.debug("*" + d)
                parts = d.split(" ")
                filename = parts[len(parts)-1]

                # retrieve file from FTPS server into memory buffer
                tempfile = io.BytesIO()
                ftp.retrbinary('RETR ' + filename, tempfile.write)
                tempfile.seek(0)
                # write file to S3
                write_file(folder + '/' + filename, tempfile)
                tempfile.close()

                # Move retrieved file
                ftp.rename(FTPUSERROOT + folder + '/' + filename, FTPUSERROOT + folder + '/success/' + filename)
    except all_errors as e:
        logger.exception(e)


def list_folder(folder):
    try:
        ftp.cwd(FTPUSERROOT + folder)
        logger.info('Changed directory to ' + ftp.pwd())

        dirlines = []
        ftp.retrlines('LIST', dirlines.append)

        for d in dirlines:
            logger.info(d)

    except all_errors as e:
        logger.exception(e)


def quit():
    try:
        ftp.quit()

    except all_errors as e:
        logger.exception(e)


# Connect and authenticate to the FTPS server
ftp = MyFTP_TLS()
ftp.connect(FTPHOST, FTPPORT)
logger.info(ftp.getwelcome())

ftp.auth()
ftp.login(FTPUSER, FTPPASSWORD)
ftp.prot_p()

# transfer pending files
s3_to_ftps('tohmrc')
ftps_to_s3('eudeltas')
ftps_to_s3('fromhmrc')

# list folder contents to check
list_folder('tohmrc')
list_folder('tohmrc/success')
list_folder('fromhmrc/success')
list_folder('eudeltas/success')

quit()