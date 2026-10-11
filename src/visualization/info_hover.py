def create_info_hover_html (hover_info_dict):
    title = hover_info_dict["title"]
    if len(title) == 0:
        title = "Info"

    title_html = f"""<h3 class="hover_title">{title}</h3>""" 

    text_html = "".join(
        f'<span class="hover_line">{line}</span>'
        for line in hover_info_dict["lines"]
    )
    
    return (
        '<div class="info_hover_holder">i</div>'
        '<div class="hover_element">'
        f'{title_html}'
        f'{text_html}'
        '</div>'
    )
