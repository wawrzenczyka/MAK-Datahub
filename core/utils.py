def get_form_error_message(form):
    form_errors = 'Invalid form\n'
    for field in form.errors:
        form_errors += f'\tField ${field} error: ${form.errors[field]}\n'
    return form_errors