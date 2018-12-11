from django import forms
from django.core.files.images import get_image_dimensions

from matchingapp.models import UserProfile

class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profileImage',)

    def clean_avatar(self):
        profileImage = self.cleaned_data['profileImage']

        try:
            '''
            w, h = get_image_dimensions(profileImage)
            #validate dimensions
            max_width = max_height = 500
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    u'Please use an image that is '
                     '%s x %s pixels or smaller.' % (max_width, max_height))
            #validate content type
            main, sub = fields.content_type.split('/')
            if not (main == 'image' and sub in ['jpeg', 'pjpeg', 'gif', 'png']):
                raise forms.ValidationError(u'Please use a JPEG, '
                    'GIF or PNG image.')
            #validate file size
            if len(fields) > (20 * 1024):
                raise forms.ValidationError(
                    u'profileImage file size may not exceed 20k.')
                    '''
        except AttributeError:
            #Handles case when we are updating the user profile and do not supply a new profileImage
            pass

        return profileImage
