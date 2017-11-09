function openEditModal(application_id, promotional_id){

    var editUrl = "/" + promotional_id + "/" + application_id + "/edit";
    $.ajax({url: editUrl, success: function(result){
        $("#editModalContent").html(result);
        $("#editModal").modal();
    }});
}

function openDeleteModal(application_id, promotional_id){

    var deleteUrl = "/" + promotional_id + "/" + application_id + "/delete";
    $.ajax({url: deleteUrl, success: function(result){
        $("#deleteModalContent").html(result);
        $("#deleteModal").modal();
    }});
}