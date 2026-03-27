import { create } from 'zustand';
import { publicApi } from '../api/publicApi';

export const useCampaignStore = create((set, get) => ({
    campaign: null,
    loading: false,
    fetchCampaign: async () => {
        // Only fetch once if already loaded to avoid multiple API calls during navigation
        if (get().campaign || get().loading) return;
        
        set({ loading: true });
        try {
            const res = await publicApi.getActiveCampaign();
            set({ campaign: res.data, loading: false });
        } catch (error) {
            console.error("Failed to fetch campaign", error);
            set({ loading: false });
        }
    },
    getMultiplier: () => {
        const campaign = get().campaign;
        return campaign ? parseFloat(campaign.multiplier) : 1.0;
    }
}));
