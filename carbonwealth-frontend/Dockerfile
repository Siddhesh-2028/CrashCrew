FROM node:20-alpine as build

WORKDIR /app
COPY carbonwealth-frontend/package.json carbonwealth-frontend/package-lock.json* ./
COPY carbonwealth-frontend/ ./

RUN npm install --silent
RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY carbonwealth-frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
