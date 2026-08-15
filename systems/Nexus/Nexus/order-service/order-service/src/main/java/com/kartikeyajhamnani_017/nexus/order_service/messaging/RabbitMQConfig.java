package com.kartikeyajhamnani_017.nexus.order_service.messaging;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.MessageDeliveryMode;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.JacksonJsonMessageConverter;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String EXCHANGE = "nexus.exchange";
    public static final String QUEUE = "inventory.order-placed.queue";
    public static final String ROUTING_KEY = "order.placed";

    @Bean
    public TopicExchange nexusExchange() {
        return new TopicExchange(EXCHANGE, true, false);
    }

    @Bean
    public Queue orderPlacedQueue() {
        return new Queue(QUEUE, true);
    }

    @Bean
    public Binding orderPlacedBinding(Queue orderPlacedQueue, TopicExchange nexusExchange) {
        return BindingBuilder.bind(orderPlacedQueue).to(nexusExchange).with(ROUTING_KEY);
    }

    @Bean
    public MessageConverter jsonMessageConverter() {
        return new JacksonJsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory, MessageConverter jsonMessageConverter) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(jsonMessageConverter);
        template.setExchange(EXCHANGE);
        template.setRoutingKey(ROUTING_KEY);
        // Spring AMQP does not default to persistent delivery - set it explicitly
        // so queued events survive a broker or consumer restart.
        template.setBeforePublishPostProcessors(message -> {
            message.getMessageProperties().setDeliveryMode(MessageDeliveryMode.PERSISTENT);
            return message;
        });
        return template;
    }
}
