
function up(){

    docker-compose -f network/docker-compose.yaml up -d
    
    echo waiting 3m for start up process
    sleep 3m
    echo finishing of start up process  
}


function down(){

    docker-compose -f network/docker-compose.yaml down --volumes --remove-orphans
}

"$@"