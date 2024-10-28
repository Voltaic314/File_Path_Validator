from FPV.Helpers._base_service import BaseService

class Egnyte(BaseService):
    # Set the maximum path length for Egnyte
    max_length = 5000
    part_length = 245

    def check_if_valid(self):
        # Call the base class check for path length and general validation
        super().check_if_valid()

        # Check length of each part
        for part in self.path_parts:
            if len(part) > self.part_length:  # Each part's length check for Egnyte
                raise ValueError(f"Path component exceeds 245 characters: \"{part}\"")

        # List of restricted names
        self.RESTRICTED_NAMES = {
            ".ds_store", 
            ".metadata_never_index", 
            ".thumbs.db", 
            "powerpoint temp", 
            "desktop.ini", 
        }

        # List of endings, starts, and other special checks
        self.ENDINGS = ['~', '._attribs_', '._rights_', '._egn_', '_egnmeta', '.tmp', '-spotlight', '.ac$', '.sv$', '.~vsdx']
        self.STARTS = ['._', '.~', 'word work file', '_egn_.', '.smbdelete']
        self.STARTS_WITH_TILDE_ENDINGS = ['.idlk', '.xlsx', '.xlsx (deleted)', '.pptx', '.pptx (deleted)']
        self.STARTS_WITH_TILDE_DOLLAR_ENDINGS = ['.doc', '.docx', '.docx (deleted)', '.rtf', '.ppt', '.pptx', '.pptx (deleted)', '.xlsm', '.xlsm (deleted)', '.sldlfp', '.slddrw', '.sldprt', '.sldasm']
        
        # Check for restricted names and additional rules
        for part in self.path_parts:
            # Check for restricted names
            if part.lower() in self.RESTRICTED_NAMES:
                raise ValueError(f"Restricted name found in path: \"{part}\"")
            
            # Check for names ending with restricted suffixes
            for ending in self.ENDINGS:
                if part.lower().endswith(ending):
                    raise ValueError(f"Name ends with restricted suffix \"{ending}\": \"{part}\"")

            # Check for names starting with restricted prefixes
            for start in self.STARTS:
                if part.lower().startswith(start):
                    raise ValueError(f"Name starts with restricted prefix \"{start}\": \"{part}\"")
                    
            # Check for names starting with '~' and ending with certain extensions
            if part.startswith('~'):
                for ending in self.STARTS_WITH_TILDE_ENDINGS:
                    if part.endswith(ending):
                        raise ValueError(f"Name starts with '~' and ends with \"{ending}\": \"{part}\"")

            # Check for names starting with '~$' and ending with certain extensions
            if part.startswith('~$'):
                for ending in self.STARTS_WITH_TILDE_DOLLAR_ENDINGS:
                    if part.endswith(ending):
                        raise ValueError(f"Name starts with '~$' and ends with \"{ending}\": \"{part}\"")

        return True
    
    def get_cleaned_path(self, raise_error: bool = True):
        cleaned_path = super().get_cleaned_path()
        # Additional cleaning for Egnyte
        cleaned_path_parts = []
        for part in cleaned_path.split('/'):

            # Remove restricted names
            for restricted_name in self.RESTRICTED_NAMES:
                if restricted_name in part.lower():
                    part = part.replace(restricted_name, '')

            # Remove endings
            for ending in self.ENDINGS:
                if part.lower().endswith(ending):
                    part = part.replace(ending, '')
            
            # Remove starts
            for start in self.STARTS:
                part = part.replace(start, '')
            
            # Remove '~' and certain endings
            if part.startswith('~'):
                for ending in self.STARTS_WITH_TILDE_ENDINGS:
                    part = part.replace(ending, '')
            
            # Remove '~$' and certain endings
            if part.startswith('~$'):
                for ending in self.STARTS_WITH_TILDE_DOLLAR_ENDINGS:
                    part = part.replace(ending, '')

            part = part.strip().rstrip(".")
            
            # lmao if there is anything left after all that hahaha...
            if part:
                cleaned_path_parts.append(part)
        
        output_path = '/'.join(cleaned_path_parts)
        output_path = output_path.strip('/')
        output_path = f'{"/" + output_path}' if not output_path.startswith("/") else output_path
        
        # Optionally check if the cleaned path is valid
        cleaned_path_instance = Egnyte(output_path)
        # this helps ensure no surprises. So that way if the supposed clean path is invalid... 
        # we can catch it here and not later on when we're trying to use it. You're welcome. :)
        if raise_error:
            cleaned_path_instance.check_if_valid()

        return cleaned_path_instance.path
            