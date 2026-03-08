import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '@/lib/api';

const CurrencyContext = createContext({
  currencyCode: 'USD',
  currencySymbol: '$',
  rateToUsd: 1,
  formatAmount: (usdAmount) => `$${Number(usdAmount).toFixed(2)}`,
});

export const useCurrency = () => useContext(CurrencyContext);

export const CurrencyProvider = ({ children }) => {
  const [currency, setCurrency] = useState({
    currencyCode: 'USD',
    currencySymbol: '$',
    rateToUsd: 1,
  });

  useEffect(() => {
    const detect = async () => {
      try {
        const resp = await apiClient.get('/currency/detect');
        const d = resp.data;
        setCurrency({
          currencyCode: d.currency_code || 'USD',
          currencySymbol: d.currency_symbol || '$',
          rateToUsd: d.rate_to_usd || 1,
        });
      } catch {
        // Default to USD on error
      }
    };
    detect();
  }, []);

  const formatAmount = (usdAmount) => {
    const converted = Number(usdAmount) * currency.rateToUsd;
    const code = currency.currencyCode;
    const sym = currency.currencySymbol;

    // For currencies with large values, no decimals
    if (['JPY', 'KRW', 'VND', 'IDR', 'NGN', 'CLP', 'COP', 'HUF'].includes(code)) {
      return `${sym}${Math.round(converted).toLocaleString()}`;
    }
    return `${sym}${converted.toFixed(2)}`;
  };

  return (
    <CurrencyContext.Provider value={{ ...currency, formatAmount }}>
      {children}
    </CurrencyContext.Provider>
  );
};
