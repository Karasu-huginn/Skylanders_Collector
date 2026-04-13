import { Link } from "react-router";
import type { Item, ItemType } from "../types";
import './ItemCard.css'
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

interface ItemCardProps {
    item: Item;
    index?: number;
}

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

const typeClasses: Record<ItemType, string> = {
    "Skylander": "type-skylander",
    "Giant": "type-giant",
    "Traptanium Crystal Trap": "type-trap",
    "Swapper": "type-swapper",
    "Vehicle": "type-vehicle",
    "Sensei": "type-sensei",
    "Villain Sensei": "type-villain",
}

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

export function ItemCard({ item, index = 0 }: ItemCardProps) {
    const { mutate } = useMutation({ mutationFn: patchCount });
    const typeClass = typeClasses[item.type.name as ItemType] || "";
    const [itemCount, setItemCount] = useState(item.count);

    const updateCount = (count_add: number) => {
        mutate({ itemId: item.id, newCount: count_add })
        setItemCount(itemCount + count_add);
    }

    return (
        <div
            className={`card ${typeClass}`}
            style={{ '--card-index': index } as React.CSSProperties}
        >
            <div className="card-type-bar" />
            <Link to={`/item/${item.id}`} className="card-body">
                <div className="card-header">
                    {item.element && elementIconMap[item.element.name] && (
                        <img
                            src={`/assets/icons/${elementIconMap[item.element.name]}`}
                            alt={item.element.name}
                            className="card-element-icon"
                        />
                    )}
                    <div className="card-info">
                        <h3 className="card-name">{item.name}</h3>
                        <span className="card-variant">{item.variant.name}</span>
                    </div>
                </div>
                <div className="card-image-wrap">
                    <div className="card-image-glow" />
                    {item.image && (
                        <img
                            src={`/assets/${item.image}`}
                            alt={item.name}
                            className="card-image"
                        />
                    )}
                </div>
            </Link>
            <div className="card-footer">
                <div className="card-count-controls">
                    <button className="count-btn count-minus" onClick={() => updateCount(-1)}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                            <path d="M5 12h14" />
                        </svg>
                    </button>
                    <span className={`count-value ${itemCount > 0 ? "has-items" : ""}`}>
                        {itemCount}
                    </span>
                    <button className="count-btn count-plus" onClick={() => updateCount(1)}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                            <path d="M12 5v14M5 12h14" />
                        </svg>
                    </button>
                </div>
                <img
                    src={`/assets/logos/${editionLogoMap[item.edition.name]}`}
                    alt={item.edition.name}
                    className="card-edition-logo"
                />
            </div>
        </div>
    );
}
