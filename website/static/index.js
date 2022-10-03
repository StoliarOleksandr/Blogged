function like(postId){
    const likeCount = document.getElementById(`likes-count-${postId}`);
    const likeButton = document.getElementById(`like-button-${postId}`);

        fetch(`/like-post/${postId}`, {method: 'POST'}).then((res) => res.json()).then((data) => {
            likeCount.innerHTML = data["likes"];
            if (data["liked"] === true) {
                likeButton.className = "fas fa-solid fa-heart";
            } else {
                likeButton.className = "far fa-heart";
            }
        }).catch((e) => alert("Could not like post."))
}

// function commentLike(commentId){
//     const likeCount = document.getElementById(`likes-count-${commentId}`);
//     const likeButton = document.getElementById(`likee-button-${commentId}`);
//
//         fetch(`/like-comment/${commentId}`, {method: 'POST'}).then((res) => res.json()).then((data) => {
//             likeCount.innerHTML = data["likes"];
//             if (data["liked"] === true) {
//                 likeButton.className = "fas fa-solid fa-heart";
//             } else {
//                 likeButton.className = "far fa-heart";
//             }
//         }).catch((e) => alert("Could not like comment"))
// }