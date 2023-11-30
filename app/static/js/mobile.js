if (/Android|webOS|iPhone|iPod|BlackBerry/i.test(navigator.userAgent)) {
    bar = document.getElementById("page-bar-pc")
    if (bar != null) {
        bar.style.display = 'none'
    }
    let tds = document.getElementsByClassName("time_col")
    for (let i = 0; i < tds.length; i++) {
        tds[i].style.display = 'none'
    }
    let spans = document.getElementById("span-br")
    if (spans != null) {
        spans.innerHTML = '<br>'
    }
} else {
    bar = document.getElementById("page-bar-mobile")
    if (bar != null) {
        bar.style.display = 'none'
    }
}
