//handle result notes
    function update_note(result_id, note_val) {
    $.ajax({
        type: "POST",
        url: '/result/'+result_id+'/notes',
        data: JSON.stringify({
                    notes: note_val
                }),
        success: null,
        contentType: "application/json"
        });
    }

    function update_note_handler(ev)
    {
        result_id = ev.target.id.split("-")[0]
        update_note(result_id, ev.target.value)
    }

    fields = document.getElementsByClassName("agg-note-field")
    for(let i = 0; i<fields.length; i++)
    {
        fields[i].addEventListener("change", update_note_handler)
    }

    //handle switching rendered md to editable

    function get_result_notes_raw(text_element, subject_id)
    {
        $.ajax({
        type: "GET",
        url: '/result/'+subject_id+'/notes_raw',
        success: function(data){
            text_element.value = data.note
            text_element.setAttribute("rows", Math.min(data.note.split("\n").length, 8))
            text_element.focus()
        },
        contentType: "application/json"
        });
    }

    function create_editable_note_field(parent, result_id)
    {
        let text_area = document.createElement("textarea")
        text_area.setAttribute("id", result_id+"-notes")
        text_area.setAttribute("class", "agg-note-field")
        text_area.addEventListener("change", update_note_handler)
        get_result_notes_raw(text_area, result_id)
        parent.appendChild(text_area)
    }
    
    fields = document.getElementsByClassName("agg-note-field-rendered")
    for(let i = 0; i<fields.length; i++)
    {
        fields[i].addEventListener("click", function(ev)
        {
            ev.preventDefault()
            let real_target = ev.target.closest(".agg-note-field-rendered")
            let result_id = real_target.id.split("-")[0]
            create_editable_note_field(real_target.parentElement, result_id)
            real_target.remove()
        })
    }

    //handle subject notes
    function update_subj_note(subject_id, note_val) {
    $.ajax({
        type: "POST",
        url: '/subject/'+subject_id+'/notes',
        data: JSON.stringify({
                    notes: note_val
                }),
        success: null,
        contentType: "application/json"
        });
    }

    function update_subj_note_handler(ev)
    {
        ev.preventDefault()
        subject_id = ev.target.id.split("-")[0]
        update_subj_note(subject_id, ev.target.value)
    }

    fields = document.getElementsByClassName("agg-subj-note-field")
    for(let i = 0; i<fields.length; i++)
    {
        fields[i].addEventListener("change", update_subj_note_handler)
    }

    //handle switching rendered subject md to editable

    function get_subject_notes_raw(text_element, subject_id)
    {
        $.ajax({
        type: "GET",
        url: '/subject/'+subject_id+'/notes_raw',
        success: function(data){
            text_element.value = data.note
            text_element.setAttribute("rows", Math.min(data.note.split("\n").length, 8))
            text_element.focus()
        },
        contentType: "application/json"
        });
    }

    function create_editable_subject_note_field(parent, subject_id)
    {
        let text_area = document.createElement("textarea")
        text_area.setAttribute("id", subject_id+"-notes")
        text_area.setAttribute("class", "agg-subj-note-field")
        text_area.addEventListener("change", update_subj_note_handler)
        get_subject_notes_raw(text_area, subject_id)
        parent.appendChild(text_area)
    }
    
    fields = document.getElementsByClassName("agg-subj-note-field-rendered")
    for(let i = 0; i<fields.length; i++)
    {
        fields[i].addEventListener("click", function(ev)
        {
            ev.preventDefault()
            let real_target = ev.target.closest(".agg-subj-note-field-rendered")
            let subject_id = real_target.id.split("-")[0]
            create_editable_subject_note_field(real_target.parentElement, subject_id)
            real_target.remove()
        })
    }