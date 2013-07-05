function sendPoodleForm(){
    $('#poodleForm [name="form.button.Save"]').live("click", function(e){
            e.stopPropagation();
            e.preventDefault();
            var infos = $("#"+this.id).closest('form#poodleForm').serializeArray();
            var base_href = $('base')[0].href;
            $.post(base_href+'/$_submit_data', infos, function(callback){
                $.post(base_href+'/ftw_poodle_table', infos, function(data){
                    $('#poodltablewrapper_'+infos[infos.length -1].value).html(data);
                });
            });
        });

}
$(sendPoodleForm);
