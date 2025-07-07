
function load_filter()
{
    try
    {
        document.filter_obj = JSON.parse($("#filter_info_div")[0].innerText);
        return
    }
    catch{}
    try{
        const urlParams = new URLSearchParams(window.location.search)
        let filter_param = urlParams.get('filter')
        if(filter_param !== null)
        {
            document.filter_obj = JSON.parse(filter_param);
        }
        return;
    }
    catch{}
    document.filter_obj = {}
}

function set_filter(filter_obj)
{
    document.filter_obj = filter_obj
    let urlParams = new URLSearchParams(window.location.search)
    let new_filter = JSON.stringify(document.filter_obj)
    urlParams.set('filter', new_filter)
    window.location.search = urlParams;
}

function pagination_set_page(page)
{
    if(page<0)
        page = 0
    if(!document.filter_obj.pagination)
        document.filter_obj.pagination = {"page": page, "per_page": 20}
    else
        document.filter_obj.pagination.page = page
    refresh_filter()
}

function pagination_get_page()
{
    if(!document.filter_obj.pagination)
        return 1
    else if(!document.filter_obj.pagination.page)
        return 1
    return document.filter_obj.pagination.page
}

function pagination_forward()
{
    pagination_set_page(pagination_get_page()+1)
}

function pagination_backward()
{
    pagination_set_page(pagination_get_page()-1)
}

function set_search_term(term)
{
    document.filter_obj.search = {"term": term}
    refresh_filter()
}

function get_filter_tag_ids()
{
    if(!document.filter_obj.tag_filter)
        return []
    if(!document.filter_obj.tag_filter.tags)
        return []
    return document.filter_obj.tag_filter.tags
}

function set_filter_tag_ids(tag_ids)
{
    document.filter_obj.tag_filter = {"tags": tag_ids}
    refresh_filter()
}

function add_filter_tag(tag_id)
{
    let arr = get_filter_tag_ids()
    arr.push(tag_id)
    set_filter_tag_ids(arr)
}

function remove_filter_tag(tag_id)
{
    let arr = get_filter_tag_ids()
    arr = arr.filter(item => item !== tag_id)
    set_filter_tag_ids(arr)
}

function refresh_filter()
{
    set_filter(document.filter_obj)
}

function search_submit(evt)
{
    console.info("submitted")
    evt.preventDefault();
    set_search_term($('#search-bar-val').val())
}

load_filter()
console.info(document.filter_obj)

/*If there is a search bar hook it up properly*/
try
{
    $('#search-bar')[0].addEventListener("submit", search_submit);
}catch{}