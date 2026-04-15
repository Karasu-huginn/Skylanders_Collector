import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router";
import { ItemCard } from "./components/ItemCard";
import type { ItemsListResponse } from "./types";
import "./ItemSearch.css";

export function ItemSearch() {
    const [search, setSearch] = useState("");
    const [page, setPage] = useState(1);
    const [isCaptured, setIsCaptured] = useState(false);
    const [isUncaptured, setIsUncaptured] = useState(false);
    const [isDuplicate, setIsDuplicate] = useState(false);
    const { isLoading, isError, error, data, refetch } = useQuery<ItemsListResponse>({
        queryKey: ['item_search', search, page, isCaptured, isUncaptured, isDuplicate],
        queryFn: async () => {
            const res = await fetch(`/api/items?search=${search}&page=${page}&limit=12&is_captured=${isCaptured}&is_uncaptured=${isUncaptured}&is_duplicate=${isDuplicate}`);
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
        },
        staleTime: 1000 * 60 * 5,
    });

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        refetch();
    }

    const changePage = (page_add: number) => {
        setPage(page + page_add);
        refetch();
    }

    const filterCount = (state_captured: boolean, state_uncaptured: boolean, state_duplicate: boolean) => {
        setIsCaptured(state_captured);
        setIsUncaptured(state_uncaptured);
        setIsDuplicate(state_duplicate);
        setPage(1);
    }

    return (
        <div className="search-page container">
            <div className="search-header">
                <Link to="/" className="search-back">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M19 12H5M12 19l-7-7 7-7" />
                    </svg>
                </Link>
                <h1 className="search-page-title">Collection</h1>
            </div>

            <form onSubmit={handleSearch} className="search-controls">
                <div className="search-input-wrap">
                    <svg className="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8" />
                        <path d="m21 21-4.3-4.3" />
                    </svg>
                    <input
                        type="text"
                        placeholder="Rechercher un Skylander..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
                <div className="search-filters">
                    <button
                        type="button"
                        className={`filter-chip ${isCaptured ? "active" : ""}`}
                        onClick={() => filterCount(!isCaptured, false, false)}
                    >
                        <span className="filter-chip-dot" />
                        Capturés
                    </button>
                    <button
                        type="button"
                        className={`filter-chip ${isUncaptured ? "active" : ""}`}
                        onClick={() => filterCount(false, !isUncaptured, false)}
                    >
                        <span className="filter-chip-dot" />
                        À capturer
                    </button>
                    <button
                        type="button"
                        className={`filter-chip ${isDuplicate ? "active" : ""}`}
                        onClick={() => filterCount(false, false, !isDuplicate)}
                    >
                        <span className="filter-chip-dot" />
                        Doublons
                    </button>
                </div>
            </form>

            {isLoading && <div className="loading-state">Chargement...</div>}
            {isError && <div className="error-state">Erreur : {(error as Error).message}</div>}
            {data && (
                <div className="results-grid">
                    {data.items.length > 0 ? (
                        data.items.map((result, index) => (
                            <ItemCard key={result.id} item={result} index={index} />
                        ))
                    ) : (
                        <div className="results-empty">
                            <h3>Aucun résultat trouvé</h3>
                            <p>Essayez d'ajuster vos critères de recherche.</p>
                        </div>
                    )}
                </div>
            )}

            {data && (page > 1 || data.items.length === 12) && (
                <div className="pagination">
                    {page > 1 && (
                        <button className="pagination-btn" onClick={() => changePage(-1)}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M19 12H5M12 19l-7-7 7-7" />
                            </svg>
                            Précédent
                        </button>
                    )}
                    <span className="pagination-page">Page {page}</span>
                    {data.items.length === 12 && (
                        <button className="pagination-btn" onClick={() => changePage(1)}>
                            Suivant
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M5 12h14M12 5l7 7-7 7" />
                            </svg>
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
