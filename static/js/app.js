const sideBarNav = document.getElementById('sidebar-nav')
const menuBtn = document.getElementById('menu-btn')
const ellipsisBtn = document.getElementById('ellipsis-btn')
const ellipsisMenu = document.getElementById('ellipsis-menu')
const searchBtn = document.getElementById('search-btn')
const searchInput = document.getElementById('search-input')

const attendancePerClassBarChart  = document.getElementById('barchart-attendance-per-class')
const teachersNoPerDepartmentBarChart = document.getElementById('barchart-teachersNo-per-department')
const studentsNoPerClassBarChart = document.getElementById('barchart-studentsNo-per-class')

const cat1Results = document.getElementById('cat1-results')
const cat2Results = document.getElementById('cat2-results')
const EndTermResults = document.getElementById('endterm-results')
const cat1Btn = document.getElementById('cat1-btn')
const cat2Btn = document.getElementById('cat2-btn')
const EndTermBtn= document.getElementById('endterm-btn')

const selectGraph = document.getElementById('choose-graph')

if(cat1Btn) {
    cat1Btn.addEventListener('click', () => {
        EndTermResults.classList.add('hidden')
        cat2Results.classList.add('hidden')
        cat1Results.classList.remove('hidden')
        EndTermBtn.classList.remove('active-btn')
        cat2Btn.classList.remove('active-btn')
        cat1Btn.classList.add('active-btn')
    })
}

if(cat2Btn) {
    cat2Btn.addEventListener('click', () => {
        EndTermResults.classList.add('hidden')
        cat1Results.classList.add('hidden')
        cat2Results.classList.remove('hidden')
        cat1Btn.classList.remove('active-btn')
        EndTermBtn.classList.remove('active-btn')
        cat2Btn.classList.add('active-btn')


    })
}

if(EndTermBtn) {
    EndTermBtn.addEventListener('click', () => {
        cat2Results.classList.add('hidden')
        cat1Results.classList.add('hidden')
        EndTermResults.classList.remove('hidden')
        cat1Btn.classList.remove('active-btn')
        cat2Btn.classList.remove('active-btn')
        EndTermBtn.classList.add('active-btn')

        
    })
}

if(selectGraph) {
    selectGraph.addEventListener('change', function () {
            let selectedGraph = this.value
            console.log("Selected value: ", selectedGraph)
            
            if(selectedGraph == 'attendance-per-class') {
                teachersNoPerDepartmentBarChart.classList.add('hidden')
                studentsNoPerClassBarChart.classList.add('hidden')
                attendancePerClassBarChart.classList.remove('hidden')
            }
            else if(selectedGraph == 'teachers-per-department'){
                studentsNoPerClassBarChart.classList.add('hidden')
                attendancePerClassBarChart.classList.add('hidden')
                teachersNoPerDepartmentBarChart.classList.remove('hidden')
            }
            else if(selectedGraph == 'number-of-students-per-class'){
                teachersNoPerDepartmentBarChart.classList.add('hidden')
                attendancePerClassBarChart.classList.add('hidden')
                studentsNoPerClassBarChart.classList.remove('hidden')
            }
        

    })
}

if(menuBtn){
    menuBtn.addEventListener('click', () => {
        sideBarNav.classList.toggle('hidden')
        sideBarNav.classList.add('flex')
    })
}

if(ellipsisBtn) {
    ellipsisBtn.addEventListener('click', () => {
        
        if(!searchInput.classList.contains('hidden')){
            searchInput.classList.add('hidden')
        }
        ellipsisMenu.classList.toggle('hidden')
        ellipsisMenu.classList.toggle('flex')
        
    })
}

if(searchBtn) {
    searchBtn.addEventListener('click', () => {
        ellipsisMenu.classList.add('hidden')
        searchInput.classList.toggle('hidden')
        
    })
}




