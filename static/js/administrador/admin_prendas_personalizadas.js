(() => {
    const orderList = document.getElementById("customOrderList");
    if (!orderList) return;

    const cards = Array.from(orderList.querySelectorAll(".custom-order-card"));
    const searchInput = document.getElementById("customSearchInput");
    const stateFilter = document.getElementById("customStateFilter");
    const sortFilter = document.getElementById("customSortFilter");
    const visibleCount = document.getElementById("customVisibleCount");
    const filterEmpty = document.getElementById("customFilterEmpty");
    const clearFiltersBtn = document.getElementById("customClearFilters");

    const paginationStage = document.getElementById("customOrdersPagination");
    const paginationInfo = document.getElementById("customPaginationInfo");
    const pageNumbers = document.getElementById("customPageNumbers");
    const prevButton = document.getElementById("customPagePrev");
    const nextButton = document.getElementById("customPageNext");

    if (!searchInput || !stateFilter || !sortFilter || cards.length === 0) return;

    const ITEMS_PER_PAGE = 4;
    const PAGINATION_THRESHOLD = 5;
    let currentPage = 1;

    const normalize = (value) =>
        String(value || "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .trim();

    const toNumber = (value) => {
        const parsed = Number(String(value || "").replace(",", "."));
        return Number.isFinite(parsed) ? parsed : 0;
    };

    const sortCards = (list) => {
        const mode = sortFilter.value || "recent";
        return [...list].sort((a, b) => {
            const indexA = Number(a.dataset.orderIndex || 0);
            const indexB = Number(b.dataset.orderIndex || 0);
            const totalA = toNumber(a.dataset.orderTotal);
            const totalB = toNumber(b.dataset.orderTotal);

            if (mode === "oldest") return indexA - indexB;
            if (mode === "total_desc") return totalB - totalA;
            if (mode === "total_asc") return totalA - totalB;
            return indexB - indexA;
        });
    };

    const renderPagination = (totalVisible) => {
        if (!paginationStage || !paginationInfo || !pageNumbers || !prevButton || !nextButton) return;

        const shouldPaginate = totalVisible >= PAGINATION_THRESHOLD;
        const totalPages = Math.max(1, Math.ceil(totalVisible / ITEMS_PER_PAGE));

        if (currentPage > totalPages) currentPage = totalPages;

        if (totalVisible === 0) {
            paginationInfo.textContent = "";
        } else if (shouldPaginate) {
            const start = (currentPage - 1) * ITEMS_PER_PAGE + 1;
            const end = Math.min(totalVisible, currentPage * ITEMS_PER_PAGE);
            paginationInfo.textContent = `Mostrando ${start} - ${end} de ${totalVisible} solicitudes`;
        } else {
            paginationInfo.textContent = `Mostrando 1 - ${totalVisible} de ${totalVisible} solicitudes`;
        }

        paginationStage.classList.toggle("d-none", !shouldPaginate || totalVisible === 0);

        pageNumbers.innerHTML = "";
        if (shouldPaginate) {
            for (let page = 1; page <= totalPages; page += 1) {
                const button = document.createElement("button");
                button.type = "button";
                button.className = `page-number${page === currentPage ? " active" : ""}`;
                button.textContent = String(page);
                button.setAttribute("aria-label", `Ir a la página ${page}`);
                button.addEventListener("click", () => {
                    if (currentPage === page) return;
                    currentPage = page;
                    render();
                });
                pageNumbers.appendChild(button);
            }
        }

        prevButton.disabled = !shouldPaginate || currentPage <= 1;
        nextButton.disabled = !shouldPaginate || currentPage >= totalPages;
    };

    const render = () => {
        const sorted = sortCards(cards);
        sorted.forEach((card) => orderList.appendChild(card));

        const query = normalize(searchInput.value);
        const state = normalize(stateFilter.value || "all");

        const filtered = sorted.filter((card) => {
            const cardState = normalize(card.dataset.orderState || "");
            const haystack = normalize(card.dataset.search || "");
            const matchesState = state === "all" || cardState === state;
            const matchesSearch = !query || haystack.includes(query);
            return matchesState && matchesSearch;
        });

        const totalVisible = filtered.length;
        const shouldPaginate = totalVisible >= PAGINATION_THRESHOLD;
        const startIndex = shouldPaginate ? (currentPage - 1) * ITEMS_PER_PAGE : 0;
        const endIndex = shouldPaginate ? startIndex + ITEMS_PER_PAGE : totalVisible;

        cards.forEach((card) => {
            card.hidden = true;
        });

        filtered.forEach((card, index) => {
            const isInCurrentPage = !shouldPaginate || (index >= startIndex && index < endIndex);
            card.hidden = !isInCurrentPage;
        });

        if (visibleCount) visibleCount.textContent = String(totalVisible);
        if (filterEmpty) filterEmpty.classList.toggle("d-none", totalVisible > 0);

        renderPagination(totalVisible);
    };

    searchInput.addEventListener("input", () => {
        currentPage = 1;
        render();
    });

    stateFilter.addEventListener("change", () => {
        currentPage = 1;
        render();
    });

    sortFilter.addEventListener("change", () => {
        currentPage = 1;
        render();
    });

    if (prevButton) {
        prevButton.addEventListener("click", () => {
            if (currentPage <= 1) return;
            currentPage -= 1;
            render();
        });
    }

    if (nextButton) {
        nextButton.addEventListener("click", () => {
            currentPage += 1;
            render();
        });
    }

    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener("click", () => {
            searchInput.value = "";
            stateFilter.value = "all";
            sortFilter.value = "recent";
            currentPage = 1;
            render();
            searchInput.focus();
        });
    }

    render();
})();
