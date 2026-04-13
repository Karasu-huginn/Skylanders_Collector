import type { Item } from "./types";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, Link } from "react-router";
import { useState, useEffect } from "react";
import "./ItemDetails.css";

const elementIconMap: Record<string, string> = {
    "Magic": "magic.png",
    "Earth": "earth.png",
    "Water": "water.png",
    "Fire": "fire.png",
    "Tech": "mechanic.png",
    "Undead": "undead.png",
    "Air": "air.png",
    "Life": "life.png",
}

const editionLogoMap: Record<string, string> = {
    "Spyro's Adventures": "SSA.png",
    "Giants": "SG.png",
    "Trap Team": "STT.png",
    "Swap Force": "SSF.png",
    "Super Chargers": "SSC.png",
    "Imaginators": "SI.png",
}

const centsToEuros = (cents: number): string => {
    if (cents === 0) return "";
    return (cents / 100).toFixed(2).replace(".", ",");
};

const eurosToCents = (value: string): number | null => {
    const trimmed = value.trim();
    if (trimmed === "") return 0;
    const parsed = parseFloat(trimmed.replace(",", "."));
    if (isNaN(parsed) || parsed < 0) return null;
    return Math.round(parsed * 100);
};

interface PatchRequest {
    itemId: number;
    newCount: number;
}

const patchCount = async (requestInfos: PatchRequest) => {
    const response = await fetch(`/api/items/${requestInfos.itemId}?count_add=${requestInfos.newCount}`, {
        method: "PATCH",
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }
    })
    return response
}

const patchPrice = async (params: { itemId: number; price: number }) => {
    const response = await fetch(`/api/items/${params.itemId}?price=${params.price}`, {
        method: "PATCH",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        },
    });
    return response;
};

export function ItemDetails() {
    const { item_id } = useParams();
    const { isLoading, isError, error, data } = useQuery<Item>({
        queryKey: ['item_details', item_id],
        queryFn: async () => {
            const res = await fetch(`/api/items/${item_id}`);
            if (!res.ok) throw new Error("Network response was not ok");
            return res.json();
        }
    });

    const { mutate } = useMutation({ mutationFn: patchCount });
    const [itemCount, setItemCount] = useState<number | null>(null);
    const displayCount = itemCount ?? data?.count ?? 0;
    const [priceInput, setPriceInput] = useState<string>("");
    const [priceSaved, setPriceSaved] = useState(false);

    useEffect(() => {
        if (data) {
            setPriceInput(centsToEuros(data.price));
        }
    }, [data]);

    const { mutate: mutatePrice } = useMutation({
        mutationFn: patchPrice,
        onSuccess: () => {
            setPriceSaved(true);
            setTimeout(() => setPriceSaved(false), 1000);
        },
    });

    const updateCount = (count_add: number) => {
        if (!data) return;
        mutate({ itemId: data.id, newCount: count_add });
        setItemCount(displayCount + count_add);
    }

    const savePrice = () => {
        if (!data) return;
        const cents = eurosToCents(priceInput);
        if (cents === null) {
            // Invalid input — revert
            setPriceInput(centsToEuros(data.price));
            return;
        }
        mutatePrice({ itemId: data.id, price: cents });
    };

    if (isLoading) {
        return <div className="detail-page container"><div className="loading-state">Chargement...</div></div>;
    }

    if (isError) {
        return <div className="detail-page container"><div className="error-state">Erreur : {(error as Error).message}</div></div>;
    }

    if (!data) return null;

    return (
        <div className="detail-page container">
            <Link to="/search" className="detail-back">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 12H5M12 19l-7-7 7-7" />
                </svg>
                Retour
            </Link>

            <div className="detail-layout">
                <div className="detail-image-section">
                    <div className="detail-image-wrap">
                        <div className="detail-image-glow" />
                        {data.image && (
                            <img
                                src={`/assets/${data.image}`}
                                alt={data.name}
                                className="detail-image"
                            />
                        )}
                    </div>
                </div>

                <div className="detail-info-section">
                    <div className="detail-title-row">
                        {data.element && elementIconMap[data.element.name] && (
                            <img
                                src={`/assets/icons/${elementIconMap[data.element.name]}`}
                                alt={data.element.name}
                                className="detail-element-icon"
                            />
                        )}
                        <div>
                            <h1 className="detail-name">{data.name}</h1>
                            <span className="detail-variant">{data.variant.name}</span>
                        </div>
                    </div>

                    <div className="detail-meta">
                        <div className="detail-meta-item">
                            <span className="detail-meta-label">Type</span>
                            <span className="detail-meta-value">{data.type.name}</span>
                        </div>
                        {data.element && (
                            <div className="detail-meta-item">
                                <span className="detail-meta-label">Élément</span>
                                <span className="detail-meta-value">{data.element.name}</span>
                            </div>
                        )}
                        <div className="detail-meta-item">
                            <span className="detail-meta-label">Édition</span>
                            <span className="detail-meta-value">{data.edition.name}</span>
                        </div>
                        <div className={`detail-meta-item detail-price-tile${priceSaved ? " detail-price-saved" : ""}`}>
                            <span className="detail-meta-label">Prix</span>
                            <div className="detail-price-input-wrap">
                                <input
                                    type="text"
                                    inputMode="decimal"
                                    className="detail-price-input"
                                    value={priceInput}
                                    placeholder="0,00"
                                    onChange={(e) => setPriceInput(e.target.value)}
                                    onBlur={savePrice}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") {
                                            e.currentTarget.blur();
                                        }
                                    }}
                                />
                                <span className="detail-price-suffix">€</span>
                            </div>
                        </div>
                    </div>

                    <div className="detail-count-section">
                        <span className="detail-count-label">Dans ta collection</span>
                        <div className="detail-count-controls">
                            <button className="detail-count-btn" onClick={() => updateCount(-1)}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                                    <path d="M5 12h14" />
                                </svg>
                            </button>
                            <span className="detail-count-value">{displayCount}</span>
                            <button className="detail-count-btn" onClick={() => updateCount(1)}>
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                                    <path d="M12 5v14M5 12h14" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <img
                        src={`/assets/logos/${editionLogoMap[data.edition.name]}`}
                        alt={data.edition.name}
                        className="detail-edition-logo"
                    />
                </div>
            </div>
        </div>
    );
}
