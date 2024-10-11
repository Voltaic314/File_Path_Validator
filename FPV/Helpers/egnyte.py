from FPV.Helpers._base_service import BaseService

class Egnyte(BaseService):
    # Set the maximum path length for Egnyte
    max_length = 5000

    def check_if_valid(self):
        # Call the base class check for path length and general validation
        super().check_if_valid()

        # Check length of each part
        for part in self.path_parts:
            if len(part) > 245:  # Each part's length check for Egnyte
                raise ValueError(f"Path component exceeds 245 characters: \"{part}\"")

        # List of restricted names
        RESTRICTED_NAMES = {
            ".ds_store", 
            ".metadata_never_index", 
            ".thumbs.db", 
            "powerpoint temp", 
            "desktop.ini", 
        }

        # List of endings, starts, and other special checks
        ENDINGS = ['~', '._attribs_', '._rights_', '._egn_', '_egnmeta', '.tmp', '-spotlight', '.ac$', '.sv$', '.~vsdx']
        STARTS = ['._', '.~', 'word work file', '_egn_.', '.smbdelete']
        STARTS_WITH_TILDE_ENDINGS = ['.idlk', '.xlsx', '.xlsx (deleted)', '.pptx', '.pptx (deleted)']
        STARTS_WITH_TILDE_DOLLAR_ENDINGS = ['.doc', '.docx', '.docx (deleted)', '.rtf', '.ppt', '.pptx', '.pptx (deleted)', '.xlsm', '.xlsm (deleted)', '.sldlfp', '.slddrw', '.sldprt', '.sldasm']
        
        # Check for restricted names and additional rules
        for part in self.path_parts:
            # Check for restricted names
            if part.lower() in RESTRICTED_NAMES:
                raise ValueError(f"Restricted name found in path: \"{part}\"")
            
            # Check for names ending with restricted suffixes
            for ending in ENDINGS:
                if part.lower().endswith(ending):
                    raise ValueError(f"Name ends with restricted suffix \"{ending}\": \"{part}\"")

            # Check for names starting with restricted prefixes
            for start in STARTS:
                if part.lower().startswith(start):
                    raise ValueError(f"Name starts with restricted prefix \"{start}\": \"{part}\"")
                    
            # Check for names starting with '~' and ending with certain extensions
            if part.startswith('~'):
                for ending in STARTS_WITH_TILDE_ENDINGS:
                    if part.endswith(ending):
                        raise ValueError(f"Name starts with '~' and ends with \"{ending}\": \"{part}\"")

            # Check for names starting with '~$' and ending with certain extensions
            if part.startswith('~$'):
                for ending in STARTS_WITH_TILDE_DOLLAR_ENDINGS:
                    if part.endswith(ending):
                        raise ValueError(f"Name starts with '~$' and ends with \"{ending}\": \"{part}\"")

        return True