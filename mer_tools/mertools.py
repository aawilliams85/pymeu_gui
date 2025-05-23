"""
   Copyright 2020 Dustin Roeder

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import olefile


class mer(object):

    def __init__(self, file):
        self.file = file

    def audit(self):
        """
        Run an audit by getting all the necessary
        information about the project

        returns a list of str
        [name, version, platform, protection status]
        """
        result = [self.get_project_name(),
                  self.get_version(),
                  self.get_platform(),
                  self.get_protection()]

        return result
    
    def dump(self):
        with olefile.OleFileIO(self.file, raise_defects=olefile.DEFECT_INCORRECT) as ole:
            ld = ole.get_metadata()
            print(ld)

    def get_version(self):
        """
        Gets the MER version

        returns version as str
        """
        with olefile.OleFileIO(self.file) as ole:
            # open the FILE_PROTECTION file
            fp = ole.openstream("VERSION_INFORMATION")
            # read the file
            data = fp.read()
        return 'v{}.{}'.format(data[1], data[2])

    def get_protection(self):

        with olefile.OleFileIO(self.file) as ole:
            # open the FILE_PROTECTION file
            fp = ole.openstream("FILE_PROTECTION")
            # read the file
            data = fp.read()
            if data[1] == 3:
                if data[3] == 0:
                    return 0, "Always allow conversion"
                elif data[3] == 1:
                    return 1, "Never allow conversion"
            elif data[1] == 1:
                return 2, "Conversion protected by password"

            return "protection unknown"

    def get_platform(self):
        """
        Gets the platform that the project is targeting
        (ME or SE)

        returns str
        """
        with olefile.OleFileIO(self.file) as ole:
            # list the directory structure of the file
            ld = ole.listdir()
        name = ''
        for item in ld:
            if item[0].endswith('.med') or item[0].endswith('.sed'):
                name = item[0]

        extension = name[-3:].lower()
        if extension == "med":
            return "FactoryTalk View Studio ME"
        elif extension == "sed":
            return "FactoryTalk View Studio SE"
        else:
            return "Unknown platform"

    def get_project_name(self):
        """
        Gets the original project name.  The MER/APA can be
        renamed yet the original project name can be different.

        returns str
        """
        with olefile.OleFileIO(self.file) as ole:
            # list the directory structure of the file
            ld = ole.listdir()
        name = ''
        for item in ld:
            if item[0].endswith('.med') or item[0].endswith('.sed'):
                name = item[0][:-4]
        return name

    def get_project_structure(self):
        """
        Gets the OLE project structure

        returns list of str
        """
        with olefile.OleFileIO(self.file) as ole:
            # list the directory structure of the file
            ld = ole.listdir()
        return ld

    def get_screen_names(self):
        """
        Gets a list of all the screen names in the project

        returns a list of str
        """
        with olefile.OleFileIO(self.file) as ole:
            # list the directory structure of the file
            ld = ole.listdir()
            screens = []
            for x in ld:
                if x[0] == 'Gfx':
                    screens.append(x[1])
        return screens

    def enable_restore(self):
        """
        Find the FILE_PROTECTION file, which contains the protection
        settings and edit it to unprotect the file
        """
        pw_string = b'\x01\x01\x00\x00\x00\x10\x00'
        protect_string = b'\x00\x03\x00\x01\x00\x00\x00'
        replace_string = b'\x00\x03\x00\x00\x00\x00\x00'
        # open the file in write mode

        protection = self.get_protection()

        with olefile.OleFileIO(self.file, write_mode=True) as ole:
            # open the FILE_PROTECTION file
            fp = ole.openstream("FILE_PROTECTION")
            # read the file
            data = fp.read()
            # unprotect it
            if protection[0] == 1:
                data = data.replace(protect_string, replace_string)
                # write the unprotected file
                ole.write_stream("FILE_PROTECTION", data)
            elif protection[0] == 2:
                data = data.replace(pw_string, replace_string)
                # write the unprotected file
                ole.write_stream("FILE_PROTECTION", data)

    def get_object(self, object_name):
        """
        Gets the raw data 
        """
        with olefile.OleFileIO(self.file) as ole:
            # open the FILE_PROTECTION file
            fp = ole.openstream(object_name)
            # read the file
            data = fp.read()
            return data
