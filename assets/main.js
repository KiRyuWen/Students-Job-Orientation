

async function getData(url,in_data_size = 15,in_search_word = "")
{
    refreshContainer();
    let params = {
        news_size: in_data_size,
    }

    if(in_search_word)
    {
        params["search"] = in_search_word;
    }
    
    const response = await fetch(url + `?${new URLSearchParams(params).toString()}`);

    if(!response.ok)
    {
        const message = `An error has occurred: ${response.status}`;
        throw new Error(message);
    }

    const data = await response.json();
    return data;
}

function displayData(data_from_api)
{
    data_from_api.then(data => {
        

        const container = document.querySelector(".container");
        const ul = document.createElement("ul");
        //container.innerHTML = "";
        container.appendChild(ul)
        ul.innerHTML = "";
        for(let i=0; i<data.length; i++)
        {
            const div = document.createElement("div");
            div.classList.add("content");
            div.innerHTML = `
            <li>
                <a href="${data[i][2]}">
                    <div class = "date">${data[i][0]}</div>
                    <div class = "title">${data[i][1]}</div>
                    <div class = "tag">${data[i][3]}</div>
                </a>
            </li>
            `;
            ul.appendChild(div);
        }
    });
}

function refreshContainer()
{
    const container = document.querySelector(".container");
    
    while(container.firstChild) //https://stackoverflow.com/questions/3955229/remove-all-child-elements-of-a-dom-node-in-javascript
    //the stackoverflow answers are arguing about how bad innerHTML is.
    //I do not know what exact answer is
    //,so I choose to remove all the children by looping
    {
        container.removeChild(container.lastChild);
    }
}

function onSearchTitle()
{
    let search_word = document.getElementById("search").value;
    let data_from_api = getData('/data',15,search_word)
    console.log('hieele')
    displayData(data_from_api)
}
function onChangeNewsSize()
{
    let news_size = document.getElementById("news_size").value;
    let data_from_api = getData('/data',news_size)
    displayData(data_from_api)
}


const data_from_api = getData('/data') //default 15, no search
displayData(data_from_api)//show to html