function openEditApplicationModal(application_id, promotional_id){
    var editUrl = "/" + promotional_id + "/" + application_id + "/edit";
    $.ajax({url: editUrl, success: function(result){
        $("#editModalContent").html(result);
        $("#editModal").modal();
    }});
}

function openDeleteApplicationModal(application_id, promotional_id){
    var deleteUrl = "/" + promotional_id + "/" + application_id + "/delete";
    $.ajax({url: deleteUrl, success: function(result){
        $("#deleteModalContent").html(result);
        $("#deleteModal").modal();
    }});
}

function openEditPromotionalModal(promotional_id){
    var editUrl = "/" + promotional_id + "/edit";
    $.ajax({url: editUrl, success: function(result){
        $("#editModalContent").html(result);
        $("#editModal").modal();
    }});
}

function openDeletePromotionalModal(promotional_id){
    var deleteUrl = "/" + promotional_id + "/delete";
    $.ajax({url: deleteUrl, success: function(result){
        $("#deleteModalContent").html(result);
        $("#deleteModal").modal();
    }});
}

function openRegisterModal(){
    var registerUrl = "/register";
    $.ajax({url: registerUrl, success: function(result){
        $("#registerModalContent").html(result);
        $("#registerModal").modal();
    }});
}
