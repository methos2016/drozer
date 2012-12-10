import binascii
import os

from mwr.common.list import chunk

class FileSystem(object):
    """
    Mercury Client Library: provides utility methods for interacting with the
    Agent's file system.
    """

    def cacheDir(self):
        """
        Get the full path to the Agent's cache directory.
        """

        return str(self.getContext().getCacheDir().toString())

    def deleteFile(self, source):
        """
        Delete a file from the Agent's file system.
        """

        file_io = self.new("java.io.File", source)

        if file_io.exists() == True:
            return file_io.delete()
        else:
            return None

    def downloadFile(self, source, destination, block_size=65536):
        """
        Copy a file from the Agent's file system to the local one.
        """

        data = self.readFile(source, block_size=block_size)

        if data:
            if os.path.isdir(destination):
                destination = os.path.sep.join([destination, source.split("/")[-1]])
                
            output = open(destination, 'w')
            output.write(str(data))
            output.close()

            return len(data)
        else:
            return None

    def exists(self, source):
        """
        Test whether or not a file exists on the Agent's file system.
        """

        file_io = self.new("java.io.File", source)

        return file_io.exists()

    def fileSize(self, source):
        """
        Get the size of a file on the Agent's file system.
        """

        file_io = self.new("java.io.File", source)

        if file_io.exists() == True:
            return file_io.length()
        else:
            return None
    
    def format_file_size(self, size):
        for x in ['bytes','KiB','MiB','GiB']:
            if size < 1024.0 and size > -1024.0:
                if x != "bytes":
                    return "%.1f %s" % (size, x)
                else:
                    return "%d %s" % (size, x)
            
            size /= 1024.0
            
        return "%3.1f%s" % (size, 'TiB')
        
    def md5sum(self, source):
        """
        Calculate the MD5 checksum of a file on the Agent's file system.
        """

        FileUtil = self.loadClass("common/FileUtil.apk", "FileUtil")

        file_io = self.new("java.io.File", source)

        if file_io.exists() == True:
            return FileUtil.md5sum(file_io)
        else:
            return None

    def readFile(self, source, block_size=65536):
        """
        Read a file from the Agent's file system, and return the data.
        """

        ByteStreamReader = self.loadClass("common/ByteStreamReader.apk", "ByteStreamReader")

        file_io = self.new("java.io.File", source)

        if file_io.exists() == True:
            file_stream = self.new("java.io.FileInputStream", file_io)

            data = ""
            
            while True:
                block = ByteStreamReader.read(file_stream, 0, block_size)
                
                if len(block) > 0:
                    data += str(block)
                else:
                    return data
        else:
            return None

    def uploadFile(self, source, destination, block_size=65536):
        """
        Copy a file from the local file system to the Agent's.
        """

        return self.writeFile(destination, open(source, 'rb').read(), block_size=block_size)

    def writeFile(self, destination, data, block_size=65536):
        """
        Write data into a file on the Agent's file system.
        """

        ByteStreamWriter = self.loadClass("common/ByteStreamWriter.apk", "ByteStreamWriter")

        file_io = self.new("java.io.File", destination)

        if file_io.exists() != True:
            file_stream = self.new("java.io.FileOutputStream", destination)

            for c in chunk(data, block_size):
                ByteStreamWriter.writeHexStream(file_stream, binascii.hexlify(c))

            file_stream.close()
            
            return len(data)
        else:
            return None
            