# -*- coding: utf-8 -*-
# Copyright (c) 2023 by wen-Huan.
# Date: 2023-03.01
# Ich und google :)
import hashlib
import win32file


class FileIdentification:
    @staticmethod
    def get_file_md5(file_path):
        """
        This method returns the MD5 hash value of a file.

        Parameters:
            file_path (str): The path of the file.

        Returns:
            str: The MD5 hash value of the file.
        """
        # Open the file for reading in binary mode
        with open(file_path, 'rb') as f:
            # Create an MD5 hash object
            md5 = hashlib.md5()

            # Read the file chunk by chunk and update the hash object
            while chunk := f.read(8192):
                md5.update(chunk)

        # Return the hexadecimal representation of the hash value
        return md5.hexdigest()

    @staticmethod
    def get_file_id(file_path):
        handle = win32file.CreateFile(file_path, 0, 0, None, win32file.OPEN_EXISTING, 0, None)
        file_info = win32file.GetFileInformationByHandle(handle)
        win32file.CloseHandle(handle)
        return file_info[8]



