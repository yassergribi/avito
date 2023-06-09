from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size_kp = 500

    if file.size > max_size_kp * 1024:
        raise ValidationError(f'files cannot be larger than {max_size_kp}KB!')
