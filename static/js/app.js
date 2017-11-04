function openEditModal(application_id, promotional_id){

    var editUrl = "/" + promotional_id + "/" + application_id + "/edit";
    $.ajax({url: editUrl, success: function(result){
        $("#editModalContent").html(result);
        $("#editModal").modal();
    }});
}