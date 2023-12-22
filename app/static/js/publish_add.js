const data_src = $('#hidden_names').val().substring(1).split(',')
const idx = $('#hidden_ids').val().substring(1).split(',')
//const data_src = ["Sauce - Thousand Island", "Wild Boar - Tenderloin", "Goat - Whole Cut"]
//const idx = ["01", "02", "03"]

const input_auto = 'autoComplete'
const input_hidden = 'order_id'
const tip = ''

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

    const info2 = document.getElementById('async-info2')
    info2.innerText = ''
    const publish_form = document.getElementById('publish_form')

    const v1 = document.getElementById('autoComplete').validity.valid
    const v2 = document.getElementById('fee').validity.valid
    const v3 = document.getElementById('area').validity.valid
    const v4 = document.getElementById('feedate').validity.valid
    const v5 = document.getElementById('pagename').validity.valid

    if (!(v1 && v2 && v3 && v4 && v5)) {
        info2.innerText = '有必填项未填'
    } else {
        const data = new FormData(publish_form);
        axios.post('/publish/add', data)
            .then(function (response) {
                if (response.data.result === 'ok') {
                    info2.innerText = '提交成功'
                    setTimeout(to_list, 1500)
                } else {
                    console.log(response.data.result)
                    info2.innerText = '提交失败'
                }
            })
    }
}


function perf_calc(fee) {
    $('#money').val((fee * 0.4).toFixed(2))
}

function to_list() {
    window.location.href = '/publish/list/1'
}