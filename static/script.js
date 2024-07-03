document.addEventListener('DOMContentLoaded', function () {
    if (window.location.pathname === '/') {
        fetchMatches();
    } else if (window.location.pathname.startsWith('/bets/')) {
        const matchId = window.location.pathname.split('/').pop();
        fetchBets(matchId);
    }
});

function fetchMatches() {
    fetch('/matches')
        .then(response => response.json())
        .then(matches => {
            const container = document.getElementById('matches-container');
            matches.forEach(match => {
                const matchElement = document.createElement('div');
                matchElement.classList.add('match');
                matchElement.innerHTML = `
                    <h2>${match.team1} vs ${match.team2}</h2>
                    <p>${match.date} - ${match.time}</p>
                    <a href="/bets/${match.id}">View Bets</a>
                `;
                container.appendChild(matchElement);
            });
        })
        .catch(error => {
            console.error('Error fetching matches:', error);
        });
}

function fetchBets(matchId) {
    fetch(`/api/bets/${matchId}`)
        .then(response => response.json())
        .then(match => {
            const container = document.getElementById('bets-container');
            const matchTitle = document.getElementById('match-title');
            matchTitle.textContent = `${match.team1} vs ${match.team2} (${match.date} - ${match.time})`;
            match.bets.forEach(bet => {
                const betElement = document.createElement('div');
                betElement.classList.add('bet');
                betElement.innerHTML = `
                    <p>Bookie: ${bet.bookie}</p>
                    <p>Bet: ${bet.bet_name} - ${bet.bet_value}</p>
                `;
                container.appendChild(betElement);
            });
        })
        .catch(error => {
            console.error('Error fetching bets:', error);
        });
}
