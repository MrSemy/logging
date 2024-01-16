class UserToFormMixin(object):
    def get_form_kwargs(self):
        kwargs = super(UserToFormMixin, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs