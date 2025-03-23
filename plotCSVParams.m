function plotCSVParams(csvFilename, xParam, yParam)
    % read the table, preserving the original column headers
    T = readtable(csvFilename, 'VariableNamingRule', 'preserve');
    
    % You must now use parentheses or braces to access columns with spaces.
    xData = T.(xParam);       % e.g. "Vehicle_Lambda" is fine (no spaces)
    yData = T.(yParam);       % e.g. "AVG DELAY" has a space, so we must use T.("AVG DELAY")
    
    figure;
    plot(xData, yData, '-o', 'LineWidth', 1.5, 'MarkerSize', 8);
    xlabel(xParam, 'FontSize', 12);
    ylabel(yParam, 'FontSize', 12);
    title(sprintf('%s vs %s', yParam, xParam), 'FontSize', 14);
    grid on;
end
