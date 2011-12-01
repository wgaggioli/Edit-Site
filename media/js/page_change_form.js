var tinymce_opts = {
    mode: "specific_textareas",
    editor_selector: 'tinymce',
    theme : "advanced",
    content_css: "/static/css/machupicchu.css",
    external_image_list_url: '/admin/editsite/page/image_list',
    document_base_url: 'http://www.machupicchuinformation.com/',
    relative_urls: false,
    gecko_spellcheck : true,
    nowrap: false,
    plugins: "paste,searchreplace,table,preview",
    plugin_preview_width : "900",
    theme_advanced_blockformats : "p,div,h1,h2,h3,h4,h5,h6,blockquote",
    theme_advanced_buttons1:"bold,italic,underline,|,justifyleft,justifycenter,justifyright,|bulllist,numlist,|,indent,outdent,sub,sup,|,cut,copy,paste,pastetext,pasteword|,undo,redo",
    theme_advanced_buttons2: "image,table,link,anchor,|,hr,sub,sup,|,forecolorpicker,backcolorpicker,|,fontselect,fontsizeselect,|,formatselect",
    theme_advanced_buttons3: "code,|,charmap, visualaid,|,search,replace,|,preview"
}
$(document).ready(function(){
    $('select#id_layout').change(function(){
        if ($(this).val()){
            data = {
                'layout_id': $(this).val(),
                'csrfmiddlewaretoken': $('[name="csrfmiddlewaretoken"]').val(),
                'page_id': $('#page_id').text()
            }
            $.post('/admin/editsite/page/layout', data, function(html){
                $('div#layout_dependent_inputs').html(html);
                tinyMCE.init(tinymce_opts);
            });
        }
    });
    $('select#id_layout').change();
    $('input#id_name').change(function(){
        var uriStr = $(this).val().toLowerCase().replace(/ /g,'-').replace(/[^\w\-]+/g,'').replace(/-{2,}/g,'-');
        $('#id_uri').val(uriStr);
    });
});
