import { Link } from "react-router";
import type { Item, ItemType } from "../types";
import './ItemCard.css'
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";

interface ItemCardProps {
    item: Item;
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

const typeColors: Record<ItemType, string> = {
    "Skylander": "type-skylander",
    "Giant": "type-giant",
    "Traptanium Crystal Trap": "type-traptanium-crystal-trap",
    "Swapper": "type-swapper",
    "Vehicle": "type-vehicle",
    "Sensei": "type-sensei",
    "Villain Sensei": "type-villain-sensei",
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

export function ItemCard(props: ItemCardProps) {
    const { mutate } = useMutation({ mutationFn: patchCount });
    const { item } = props;
    const typeColor = typeColors[item.type.name as ItemType] || "";
    const [itemCount, setItemCount] = useState(item.count);
    const updateCount = (count_add: number) => {
        mutate({ itemId: item.id, newCount: count_add })
        setItemCount(itemCount + count_add);
    }
    return <>
        <div className={`item-card ${typeColor}`}>
            <Link to={`/item/${item.id}`} className="item-card-top">
                <img src={`/assets/icons/${elementIconMap[item.element.name]}`} className="skylander-element" />
                <h1 className="skylander-name">{item.name}</h1>
                <div className="shadow">
                    <img src={`/assets/${item.image}`} className="skylander-img" />
                </div>
                <p className="skylander-variant">{item.variant.name}</p>
            </Link>
            <div className="item-card-bottom">
                <button className="skylander-count-plus" onClick={() => updateCount(1)}>+</button>
                <p className="skylander-count">{itemCount}</p>
                <button className="skylander-count-minus" onClick={() => updateCount(-1)}>-</button>
                <img src={`/assets/logos/${editionLogoMap[item.edition.name]}`} width={300} height={200} className="skylander-edition" />
            </div>
        </div>
    </>
}
