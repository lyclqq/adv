const input_auto = 'autoComplete'
const input_hidden = 'order_id'
const tip = ''
//const data_src = ["Sauce - Thousand Island", "Wild Boar - Tenderloin", "Goat - Whole Cut"]
//const idx = ["01", "02", "03"]

const data_src = $('#hidden_names').val().substring(1).split(',')
const idx = $('#hidden_ids').val().substring(1).split(',')

const autoCompleteJS = new autoComplete({
    selector: "#" + input_auto,
    placeHolder: tip,
    data: {
        src: data_src,
        cache: false,
    },
    idx: idx,
    resultsList: {
        element: (list, data) => {
            if (!data.results.length) {
                const message = document.createElement("div");
                message.setAttribute("class", "no_result");
                message.innerHTML = `<span>没找到包含 "${data.query} 的相关数据"</span>`;
                list.prepend(message);
            }
        },
        noResults: true,
    },
    resultItem: {
        highlight: true
    },
    events: {
        input: {
            selection: (event) => {
                const selection = event.detail.selection.value;
                autoCompleteJS.input.value = selection;
                document.getElementById(input_hidden).value = autoCompleteJS.idx[autoCompleteJS.data.src.indexOf(selection)]
            }
        }
    }
});

function publish_add() {
    document.getElementById('async-info2').innerText = ''
    const publish_form = document.getElementById('publish_form')

    const v1 = document.getElementById('autoComplete').validity.valid
    const v2 = document.getElementById('fee').validity.valid
    const v3 = document.getElementById('area').validity.valid
    const v4 = document.getElementById('feedate').validity.valid
    const v5 = document.getElementById('pagename').validity.valid

    if (!v1 && v2 && v3 && v4 && v5) {
        document.getElementById('async-info2').innerText = '有必填项未填'
    } else {
        const data = new FormData(publish_form);
        axios.post('/publish/add', data)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    document.getElementById('async-info2').innerText = '提交成功'
                    setTimeout(pub_modal_hide, 1500)
                    //publish_form.reset()
                    location.reload()
                } else {
                    console.log(response.data.result)
                    document.getElementById('async-info2').innerText = '提交失败'
                }
            })
    }
}

function pub_modal_hide() {
    $("#fee2Modal").modal("hide")
}

function publish_cancel(pid) {
    if (window.confirm('确定作废吗？')) {
        const data = {
            "pid": pid,
        }
        axios.post('/publish/cancel', data, config)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    console.log('操作成功')
                    location.reload()
                } else {
                    console.log('提交失败')
                }
            })
    }
}

function fee2_to_audit(pid, fee, money, filepath, filename) {
    $('#pid').val(pid)
    $('#sp_fee').text(fee)
    $('#sp_money').text(money)
    if (filename === 'None') {
        $('#sp_link').text('无附件')
    } else {
        $('#sp_link').html('<a href="/publish/download?pid=' + pid + '" target="_blank" id="filepath">' + filename + '</a>')
    }
    $("#fee2AuditModal").modal("show")
}

function publish_audit() {
    const data = {
        "pid": $('#pid').val(),
        "status": $('#status').val()
    }
    axios.post('/publish/audit', data, config)
        .then(function (response) {
            if (response.data.result === 'ok') {
                document.getElementById('async-info3').innerText = '提交成功'
                document.getElementById('publish_form_audit').reset()
                setTimeout(pub_audit_hide, 1500)
                location.reload()
            } else {
                console.log('提交失败')
            }
        })
}

function pub_audit_hide() {
    $("#fee2AuditModal").modal("hide")
}

function perf_calc(fee) {
    $('#money').val((fee * 0.4).toFixed(2))
}

function publish_query(){
    window.location.href='/publish/list/1/'+$("#qr_status").val()+'/'+$("#qr_order").val()
}