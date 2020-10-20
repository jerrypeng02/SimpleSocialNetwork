function refreshFollower() {
    $.ajax({
        url: "/socialnetwork/refresh-follower",
        dataType: "json",
        success: function(response) {
            updatePost(response.posts)
            updateComment(response.comments)
        }
    });
}

function displayError(message) {
    $(".error").html(message);
}

function updatePost(posts) {
    console.log(posts)
    $(posts).each(function() {
        let curr_id = "post_by_" + this.id
        if (document.getElementById(curr_id) == null) {
            let postTime = new Date(this.post_date_time)
            let postDisplayTime = (postTime.getMonth() + 1) + '/' + postTime.getDate()
                + '/' + postTime.getFullYear()
                + ' ' + (postTime.getHours() < 10 ? '0' : '')
                + (postTime.getHours() % 12 === 0 ? 12 : (postTime.getHours() % 12)) + ':'
                + (postTime.getMinutes() < 10 ? '0' : '')
                + postTime.getMinutes() + (postTime.getHours() < 12 ? 'AM' : 'PM');
            $("#post").prepend(
                '<li id="' + curr_id + '">' + 'Post by ' +
                '<span id="id_post_profile_' + this.id + '">' +
                '<a href="/socialnetwork/user_profile/' + this.user_id + '">' + this.name + '</a></span>' +
                ' - <span id="id_post_text_' + this.id + '">' + sanitize(this.post_text) + '</span>' +
                ' - <span id="id_post_date_time_' + this.id + '">' + postDisplayTime + '</span>' +
                '<ul id="comment_under_post_' + this.id + '"></ul>' +
                '<label>New Comment: </label>' +
                '<input type="text" id="id_comment_input_text_' + this.id + '">' +
                '<button id="id_comment_button_' + this.id + '" type="submit" onclick="addComment(' + this.id + ')">Submit</button>' +
                '<span class="error"></span>' +
                '</li>'
            )
        }
    })
}

function updateComment(comments) {
    $(comments).each(function() {
        let curr_id = "comment_by_" + this.id;
        if (document.getElementById(curr_id) == null) {
            let commentTime = new Date(this.comment_date_time);
            let commentDisplayTime = (commentTime.getMonth() + 1) + '/' + commentTime.getDate()
                + '/' + commentTime.getFullYear()
                + ' ' + (commentTime.getHours() < 10 ? '0' : '')
                + (commentTime.getHours() % 12 === 0 ? 12 : (commentTime.getHours() % 12)) + ':'
                + (commentTime.getMinutes() < 10 ? '0' : '')
                + commentTime.getMinutes() + (commentTime.getHours() < 12 ? 'AM' : 'PM');
            $("#comment_under_post_" + this.post_id).append(
                '<li id="' + curr_id + '">' + 'Commented by ' +
                    '<span id="id_comment_profile_' + this.id + '">' +
                    '<a href="/socialnetwork/user_profile/' + this.user_id + '">' + this.name + '</a></span>' +
                    ' - <span id="id_comment_text_' + this.id + '">' + sanitize(this.comment_text) + '</span>' +
                    ' - <span id="id_comment_date_time_' + this.id + '">' + commentDisplayTime + '</span>' +
                    '<span class="error"></span>' +
                '</li>'
            )
        }
    })
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
}

function addComment(post_id) {
    let commentTextElement = $("#id_comment_input_text_" + post_id)
    let commentTextValue = commentTextElement.val()

    // Clear input box and old error message (if any)
    commentTextElement.val('')
    displayError('');

    $.ajax({
        url: "/socialnetwork/add-comment",
        type: "POST",
        data: "post_id="+post_id+"&comment_text="+commentTextValue+"&csrfmiddlewaretoken="+getCSRFToken(),
        dataType : "json",
        success: function(response) {
            if(Array.isArray(response)) {
                updateComment(response)
            } else {
                displayError(response.error)
            }
        }
    });
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}

window.onload = refreshFollower;
window.setInterval(refreshFollower, 5000);